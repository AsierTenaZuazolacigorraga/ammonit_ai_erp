import json
from typing import List, Tuple, Union

from constants import *
from models import ExamBM, ExamEvaluationBM, ExerciseBM, ExerciseEvaluationBM

from commons.files import pngs_2_base64

# class Chat:

#     def __init__(
#         self,
#         client,
#         name: str,
#         model: str,
#     ) -> None:
#         self.client = client
#         self.name = name
#         self.model = model
#         self.chat_history = []
#         self.costs = COSTS
#         self.costs_history = []

#     def persistent_chat(self, user_message: list, user_metadata: dict = {}) -> str:
#         response = self.puntual_chat(user_message, user_metadata)
#         self.chat_history += user_message
#         self.chat_history += [
#             {
#                 "role": "assistant",
#                 "content": [
#                     {"type": "text", "text": response},
#                 ],
#             }
#         ]
#         return response


# class OpenAIChat(Chat):

#     def __init__(
#         self,
#         name: str,
#         model: str = "gpt-4o",
#         system_message: list = [],
#     ) -> None:
#         super().__init__(client, name, model)
#         self.chat_history = system_message

#     def puntual_chat(self, user_message: list, user_metadata: dict = {}) -> str:
#         metadata = {"name": self.name}
#         if user_metadata != {}:
#             metadata.update(user_metadata)
#         completion = self.client.chat.completions.create(
#             model=self.model,
#             messages=self.chat_history + user_message,
#             temperature=0,
#             max_tokens=2048,
#             top_p=0,
#             frequency_penalty=0,
#             presence_penalty=0,
#             stream=False,
#             response_format={"type": "text"},
#             store=True,
#             metadata=metadata,
#         )
#         response = completion.choices[0].message.content
#         costs = (
#             (self.costs[self.model]["input"] / 1e6)
#             * (
#                 completion.usage.prompt_tokens
#                 - completion.usage.prompt_tokens_details.cached_tokens
#             )
#             + (self.costs[self.model]["input_cached"] / 1e6)
#             * (completion.usage.prompt_tokens_details.cached_tokens)
#             + (self.costs[self.model]["output"] / 1e6)
#             * completion.usage.completion_tokens
#         )
#         logging.info(f"Chat for {self.name} completed correctly with costs: {costs} $")
#         self.costs_history.append(costs)

#         return response

#     def build_prompt_from_images(self, png_files: List[str]) -> List[dict]:
#         return [
#             {
#                 "type": "image_url",
#                 "image_url": {"url": f"data:image/jpeg;base64,{f}"},
#             }
#             for f in pngs_2_base64(png_files)
#         ]

#     def clear_chat(self, messages_2_keep: int) -> None:
#         self.chat_history = self.chat_history[
#             :messages_2_keep
#         ]  # Just keep the system message


# class AnthropicChat(Chat):

#     def __init__(
#         self,
#         name: str,
#         model: str = "gpt-4o",
#         system_message: str = "",
#     ) -> None:
#         super().__init__(client, name, model)
#         self.system_message = system_message

#     def puntual_chat(self, user_message: list, user_metadata: dict = {}) -> str:
#         metadata = {"user_id": self.name}
#         if user_metadata != {}:
#             metadata.update(user_metadata)
#         completion = self.client.messages.create(
#             model=self.model,
#             system=self.system_message,
#             messages=self.chat_history + user_message,
#             temperature=0,
#             max_tokens=2048,
#             top_p=0,
#             stream=False,
#             metadata=metadata,
#         )
#         response = completion.content[0].text
#         costs = (self.costs[self.model]["input"] / 1e6) * (
#             completion.usage.input_tokens
#         ) + (self.costs[self.model]["output"] / 1e6) * completion.usage.output_tokens
#         logging.info(f"Chat for {self.name} completed correctly with costs: {costs} $")
#         self.costs_history.append(costs)

#         return response

#     def build_prompt_from_images(self, png_files: List[str]) -> List[dict]:
#         return [
#             {
#                 "type": "image",
#                 "source": {"type": "base64", "media_type": "image/png", "data": f"{f}"},
#             }
#             for f in pngs_2_base64(png_files)
#         ]

#     def clear_chat(self, messages_2_keep: int) -> None:
#         self.chat_history = self.chat_history[
#             : messages_2_keep - 1
#         ]  # Just keep the system message


# class GroqChat(Chat):

#     def __init__(
#         self,
#         name: str,
#         model: str = "gpt-4o",
#         system_message: list = [],
#     ) -> None:
#         super().__init__(client, name, model)
#         self.chat_history = system_message

#     def puntual_chat_with_format(
#         self, user_message: list, base_model: BaseModel
#     ) -> str:
#         completion = self.client.chat.completions.create(
#             model=self.model,
#             messages=self.chat_history + user_message,
#             temperature=0,
#             max_tokens=2048,
#             top_p=0,
#             frequency_penalty=0,
#             presence_penalty=0,
#             stream=False,
#             response_format={"type": "json_object"},
#         )
#         response = completion.choices[0].message.content
#         costs = (self.costs[self.model]["input"] / 1e6) * (
#             completion.usage.prompt_tokens
#         ) + (
#             self.costs[self.model]["output"] / 1e6
#         ) * completion.usage.completion_tokens
#         logging.info(f"Chat for {self.name} completed correctly with costs: {costs} $")
#         self.costs_history.append(costs)

#         return base_model.model_validate(json.loads(response))


# class ExamEvaluation:

#     def __init__(
#         self,
#         exam_evaluation: ExamEvaluationBM,
#     ) -> None:
#         self.lecture = exam_evaluation.lecture
#         self.professor = exam_evaluation.professor
#         self.ids = exam_evaluation.ids
#         self.exercises = []
#         self.max_mark = 0
#         self.evaluation = ""

#     def append_exercise_evaluation(
#         self, id: int, exercise_evaluation: ExerciseEvaluationBM, evaluation: str
#     ) -> None:
#         self.exercises.append(
#             {
#                 "id": id,
#                 "max_mark": exercise_evaluation.max_mark,
#                 "evaluation": evaluation,
#             }
#         )

#     def post_evaluation(self) -> None:
#         self.max_mark = sum([e["max_mark"] for e in self.exercises])
#         self.evaluation = "\n\n".join([e["evaluation"] for e in self.exercises])


# class ExamCorrection:

#     def __init__(
#         self,
#         exam_correction: ExamBM,
#     ) -> None:
#         self.student = exam_correction.student
#         self.exercises = []
#         self.curr_mark = 0
#         self.correction = ""

#     def append_exercise_correction(
#         self, id: int, exercise_correction: ExerciseCorrectionBM, correction: str
#     ) -> None:
#         self.exercises.append(
#             {
#                 "id": id,
#                 "curr_mark": exercise_correction.curr_mark,
#                 "short_correction": exercise_correction.correction,
#                 "long_correction": correction,
#             }
#         )

#     def post_correction(self) -> None:
#         self.curr_mark = sum([e["curr_mark"] for e in self.exercises])
#         self.correction = "\n\n".join([e["long_correction"] for e in self.exercises])
