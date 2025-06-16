import base64
import io
import json
import logging
import os
import traceback
import uuid
from datetime import datetime, timezone

from app.logger import get_logger
from app.models import Prompt, PromptCreate, PromptUpdate, User
from app.repositories.base import CRUDRepository
from sqlmodel import Session

logger = get_logger(__name__)


class PromptService:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.repository = CRUDRepository[Prompt](Prompt, session)

    def get_all(self, skip: int, limit: int, owner_id: uuid.UUID) -> list[Prompt]:
        return self.repository.get_all_by_kwargs(
            skip=skip,
            limit=limit,
            **{"owner_id": owner_id},
        )

    def get_by_id(self, id: uuid.UUID) -> Prompt | None:
        return self.repository.get_by_id(id)

    def get_count(self, owner_id: uuid.UUID) -> int:
        return self.repository.count_by_kwargs(**{"owner_id": owner_id})

    def delete(self, id: uuid.UUID) -> None:
        self.repository.delete(id)

    def update(self, prompt_update: PromptUpdate, id: uuid.UUID) -> Prompt:
        prompt = self.get_by_id(id)
        if not prompt:
            raise ValueError("Prompt not found")
        return self.repository.update(
            prompt, update=prompt_update.model_dump(exclude_unset=True)
        )

    def create(self, prompt_create: PromptCreate, owner_id: uuid.UUID) -> Prompt:
        return self.repository.create(
            Prompt.model_validate(prompt_create, update={"owner_id": owner_id})
        )
