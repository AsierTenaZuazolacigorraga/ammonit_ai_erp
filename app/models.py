from typing import List, Literal

from constants import *
from pydantic import BaseModel, Field


# BaseModels
class ExerciseBM(BaseModel):
    id: int = Field(description=ID)


class ExamBM(BaseModel):
    student: str = Field(description=STUDENT)
    exercises: List[ExerciseBM]
    raw: str

    def add_raw(self, raw):
        self.raw = raw


class ExerciseEvaluationBM(BaseModel):
    id: int = Field(description=ID)
    max_mark: float = Field(description=MAX_MARK)
    type: float = Field(description=TYPE)


class ExamEvaluationBM(BaseModel):
    lecture: str = Field(description=LECTURE)
    professor: str = Field(description=PROFESSOR)
    exercises: List[ExerciseEvaluationBM]
    raw: str

    def add_raw(self, raw):
        self.raw = raw


class ExerciseCorrectionBM(BaseModel):
    id: int = Field(description=ID)
    short_just: str = Field(description=SHORT_JUST)
    mark: float = Field(description=MARK)


class ExamCorrectionBM(BaseModel):
    exercises: List[ExerciseCorrectionBM]
    raw: str

    def add_raw(self, raw):
        self.raw = raw


class YesNo(BaseModel):
    answer: Literal["yes", "no"] = Field(description="Respuesta a la pregunta")
    why: str = Field(description='Justificación de porqué la respuesta es "si" o "no"')
