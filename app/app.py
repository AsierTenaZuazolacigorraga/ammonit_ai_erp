import json
import logging
import os
import pickle
from typing import List, Tuple, Union

import logging_config  # custom logger
import pandas as pd
from anthropic import Anthropic
from classes import AnthropicChat, GroqChat, OpenAIChat
from constants import *
from dotenv import load_dotenv
from groq import Groq
from models import ExamBM, ExamCorrectionBM, ExamEvaluationBM, YesNo
from openai import OpenAI
from utils import *

load_dotenv()


def main():

    logging.info("Starting proff_ai ...")

    # Define clients
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Define chats
    evaluation_chat = AnthropicChat(
        anthropic_client,
        name="evaluator",
        model="claude-3-5-sonnet-20241022",
        system_message=EVALUATION_SYSTEM,
    )
    exams_chat = AnthropicChat(
        anthropic_client,
        name="corrector",
        model="claude-3-5-sonnet-20241022",
        system_message=EXAMS_SYSTEM,
    )
    corrections_chat = OpenAIChat(
        openai_client,
        name="corrector",
        model="gpt-4o",
        system_message=[
            {
                "role": "system",
                "content": [{"type": "text", "text": CORRECTIONS_SYSTEM}],
            }
        ],
    )
    structer_chat = GroqChat(
        groq_client,
        name="structer",
        model="llama-3.2-90b-text-preview",
        system_message=[
            {
                "role": "system",
                "content": STRUCTURER_SYSTEM,
            }
        ],
    )

    if IS_EVALUATION:

        logging.info("Retrieve evaluation")

        # Process professor
        professor_pdf_file = merge_pdfs(PROFESSOR_PDF_FOLDER, PROFESSOR_PDF_FILE)
        professor_png_files = pdf_2_pngs(
            professor_pdf_file,
            PROFESSOR_PNG_FOLDER,
        )

        # # Load files
        # for file in openai_client.files.list().data:
        #     openai_client.files.delete(file.id)
        # professor_openai_files = []
        # for file in professor_png_files:
        #     professor_openai_files.append(
        #         openai_client.files.create(
        #             file=open(file, "rb"),
        #             purpose="vision",
        #         )
        #     )

        exam_evaluation_raw = evaluation_chat.persistent_chat(
            [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": EVALUATION_USER},
                    ]
                    + evaluation_chat.build_prompt_from_images(professor_png_files),
                }
            ],
        )
        exam_evaluation = structer_chat.puntual_chat_with_format(
            [
                {
                    "role": "user",
                    "content": STRUCTURER_USER.format(
                        base_text=exam_evaluation_raw,
                        base_json_schema=json.dumps(
                            ExamEvaluationBM.model_json_schema(), indent=2
                        ),
                    ),
                }
            ],
            ExamEvaluationBM,
        )
        exam_evaluation.add_raw(exam_evaluation_raw)

        logging.info(f"Total cost for evaluation: {sum(evaluation_chat.costs_history)}")

        logging.info("Save eval info to file ...")
        with open(EVAL_RESPONSE, "wb") as f:
            pickle.dump(exam_evaluation, f)
        with open(EVAL_RESPONSE_RAW, "w") as f:
            f.write(exam_evaluation.raw)

    else:
        logging.info("Load eval info to file ...")
        with open(EVAL_RESPONSE, "rb") as f:
            exam_evaluation = pickle.load(f)

    if IS_EVALUATION_REVIEW:

        logging.info(
            "Fine tune the evaluation criteria, modify and save the raw file. Press enter to continue ..."
        )
        input()
        with open(EVAL_RESPONSE_RAW, "r") as f:
            exam_evaluation.add_raw(f.read())
        with open(EVAL_RESPONSE, "wb") as f:
            pickle.dump(exam_evaluation, f)

    if IS_EXAMS:

        logging.info("Retrieve exams")

        # Process students
        students_pdf_file = merge_pdfs(STUDENTS_PDF_FOLDER, STUDENTS_PDF_FILE)
        students_png_files = pdf_2_pngs(
            students_pdf_file,
            STUDENTS_PNG_FOLDER,
        )
        students_pngs_files = organise_students_pngs(students_png_files)

        # Iterate, consult, and store each exam
        exams = []
        for i, students_png_files in enumerate(students_pngs_files):

            logging.info(f"Retrieve correction for student {i}")

            exams_chat.clear_chat(messages_2_keep=2)
            exam_raw = exams_chat.persistent_chat(
                [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": EXAMS_USER},
                        ]
                        + exams_chat.build_prompt_from_images(students_png_files),
                    }
                ]
            )
            exam = structer_chat.puntual_chat_with_format(
                [
                    {
                        "role": "user",
                        "content": STRUCTURER_USER.format(
                            base_text=exam_raw,
                            base_json_schema=json.dumps(
                                ExamBM.model_json_schema(), indent=2
                            ),
                        ),
                    }
                ],
                ExamBM,
            )
            exam.add_raw(exam_raw)
            exams.append(exam)

        logging.info(f"Total cost for exam retrieval: {sum(exams_chat.costs_history)}")

        logging.info("Save exam retrieval to file ...")
        with open(EXAMS_RESPONSE, "wb") as f:
            pickle.dump(exams, f)
        with open(EXAMS_RESPONSE_RAW, "w") as f:
            f.write("\n\n".join([e.raw for e in exams]))

    else:
        logging.info("Load eexam retrieval from file ...")
        with open(EXAMS_RESPONSE, "rb") as f:
            exams = pickle.load(f)

    # Construct correction
    if IS_CORRECTIONS:

        logging.info("Retrieve corrections")

        corrections = []
        for exam in exams:

            logging.info(f"Retrieve correction for student {exam.student}")

            corrections_chat.clear_chat(messages_2_keep=3)
            correction_raw = corrections_chat.persistent_chat(
                [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": CORRECTIONS_USER.format(
                                    PROFESSOR_EXAM=exam_evaluation.raw,
                                    STUDENT_EXAM=exam.raw,
                                ),
                            },
                        ],
                    }
                ]
            )
            correction = structer_chat.puntual_chat_with_format(
                [
                    {
                        "role": "user",
                        "content": STRUCTURER_USER.format(
                            base_text=correction_raw,
                            base_json_schema=json.dumps(
                                ExamCorrectionBM.model_json_schema(), indent=2
                            ),
                        ),
                    }
                ],
                ExamCorrectionBM,
            )
            correction.add_raw(correction_raw)
            corrections.append(correction)

        logging.info(
            f"Total cost for exam corrections: {sum(corrections_chat.costs_history)}"
        )

        logging.info("Save exam corrections to file ...")
        with open(CORRECTIONS_RESPONSE, "wb") as f:
            pickle.dump(corrections, f)
        with open(CORRECTIONS_RESPONSE_RAW, "w") as f:
            f.write("\n\n".join([c.raw for c in corrections]))

    else:
        logging.info("Load exam corrections from file ...")
        with open(CORRECTIONS_RESPONSE, "rb") as f:
            corrections = pickle.load(f)

    logging.info(
        f"Total cost for evaluation, exam retrieve, and correction: {sum(evaluation_chat.costs_history) + sum(exams_chat.costs_history) + sum(corrections_chat.costs_history)}"
    )

    # Adapt the base corrections for more complete info
    logging.info(f"Exporting all info to report ...")
    data = []
    for i in range(len(corrections)):
        for j in range(len(corrections[i].exercises)):
            data.append(
                {
                    "id": corrections[i].exercises[j].id,
                    "max_mark": exam_evaluation.exercises[j].max_mark,
                    "mark": corrections[i].exercises[j].mark,
                    "correction": corrections[i].exercises[j].short_just,
                    "lecture": exam_evaluation.lecture,
                    "student": exams[i].student,
                }
            )
        total_mark = sum(
            [
                d["mark"]
                for d in data
                if d["lecture"] == exam_evaluation.lecture
                and d["student"] == exams[i].student
            ]
        )
        [
            d.update(
                {
                    "total_mark": total_mark,
                }
            )
            for d in data
            if d["lecture"] == exam_evaluation.lecture
            and d["student"] == exams[i].student
        ]
    df = pd.DataFrame(data)
    df.insert(0, "lecture", df.pop("lecture"))
    df.insert(1, "student", df.pop("student"))
    df.insert(2, "total_mark", df.pop("total_mark"))

    # Export to Excel without formatting first
    df.to_excel(CORRECTIONS_REPORT_FILE, index=False)


if __name__ == "__main__":
    main()
