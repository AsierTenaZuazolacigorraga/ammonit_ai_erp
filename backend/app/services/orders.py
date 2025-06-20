import asyncio
import base64
import io
import json
import os
import pprint
import tempfile
import uuid
from datetime import datetime, timezone
from io import BytesIO, StringIO
from typing import List, Union
from uuid import UUID

import pandas as pd
import PyPDF2
from app.core.config import settings
from app.logger import get_logger
from app.models import Email, Order, OrderCreate, OrderState, OrderUpdate, User
from app.repositories.base import CRUDRepository
from app.services.ai import AiService
from app.services.users import UserService
from dotenv import load_dotenv
from fastapi import HTTPException
from groq import Groq
from llama_parse import LlamaParse, ResultType
from openai import OpenAI
from pdf2image import convert_from_bytes
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlmodel import Session

load_dotenv()

logger = get_logger(__name__)


def parse_pdf_binary_2_base64_jpg(pdf_binary: bytes) -> str:
    # Convert PDF to images (one per page)
    images = convert_from_bytes(pdf_binary)
    # Take the first page (or loop through all if needed)
    img = images[0]
    # Save image to a BytesIO buffer in JPG format
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    # Encode the image bytes as base64
    img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    return img_base64


def parse_pdf_binary_2_base64(pdf_binary: bytes) -> str:
    return base64.b64encode(pdf_binary).decode("utf-8")


async def parse_document_2_md(
    ai_service: AiService, document: bytes, document_name: str, user: User
) -> str:

    # Convert to md
    if not document_name.endswith(".pdf"):
        raise ValueError(f"Unsupported file type: {document_name}")

    response = ai_service.response_create_basic(
        "document_2_md",
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{parse_pdf_binary_2_base64_jpg(document)}",
                }
            ],
        },  # type: ignore
        user=user,
    )
    md = response.output_text
    if md is None:
        raise ValueError("Failed to parse the PDF to markdown.")
    return md


async def parse_md_2_order(ai_service: AiService, md: str, user: User) -> dict:

    response = ai_service.response_create_basic(
        "md_2_order",
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": md,
                }
            ],
        },
        user=user,
        find_and_replace={
            "{ADDITIONAL_RULES}": user.orders_additional_rules or "",
            "{PARTICULAR_RULES}": user.orders_particular_rules or "",
        },
    )
    order = response.output_text
    if order is None:
        raise ValueError("Failed to parse the markdown to order.")

    # Extract structured info
    response = ai_service.response_create_basic(
        "order_2_json",
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": order,
                }
            ],
        },
        user=user,
    )
    if response.output_text is None:
        raise ValueError("Failed to parse the order information from the markdown.")

    return json.loads(response.output_text)


def parse_order_dict_2_csv(order_dict: dict) -> str:

    # Find keys that contain lists of dictionaries
    list_keys = []
    for key, value in order_dict.items():
        if isinstance(value, list) and value and isinstance(value[0], dict):
            list_keys.append(key)

    # If we found any keys with lists of dictionaries
    if list_keys:
        # Create a list to hold all rows
        rows = []

        # Extract common fields from the order (non-list fields)
        common_fields = {k: v for k, v in order_dict.items() if k not in list_keys}

        # For each list key, process its items
        for list_key in list_keys:
            for item in order_dict[list_key]:
                row = common_fields.copy()
                row.update(item)
                rows.append(row)

        # Create DataFrame from the rows
        df = pd.DataFrame(rows)

    # If the order doesn't have any list keys
    else:
        raise ValueError("Order doesn't have any list keys")

    return df.to_csv(sep=";", index=False)


async def process(
    order_create: OrderCreate, ai_service: AiService, user: User
) -> tuple[User, OrderCreate]:

    if order_create.base_document is None:
        raise ValueError("Base document cannot be None")
    if order_create.base_document_name is None:
        raise ValueError("Base document name cannot be None")

    # Preprocess document
    document = preprocess_document(
        order_create.base_document, order_create.base_document_name, user
    )

    # Parse document to md
    md = await parse_document_2_md(
        ai_service, document, order_create.base_document_name, user
    )

    # Parse md to order
    order_dict = await parse_md_2_order(ai_service, md, user)

    # Preprocess order
    order_columns_mapping = ai_service.get_prompt("order_columns_mapping").structure
    if order_columns_mapping is None:
        raise ValueError("Order columns mapping cannot be None")
    order_create.content_processed = preprocess_order(
        order_columns_mapping, order_dict, user
    )
    order_create.content_structured = order_dict
    order_create.base_document_markdown = md

    return user, order_create


def preprocess_document(document: bytes, document_name: str, user: User) -> bytes:
    from app.services._orders._preprocessors_documents import _preprocess_document

    return _preprocess_document(document, document_name, user)


def preprocess_order(order_columns_mapping: dict, order_dict: dict, user: User) -> str:
    from app.services._orders._preprocessors_orders import _preprocess_order

    return parse_order_dict_2_csv(
        _preprocess_order(order_columns_mapping, order_dict, user)
    )


class OrderService:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.repository = CRUDRepository[Order](Order, session)
        self.user_service = UserService(session)
        self.ai_service = AiService(session)
        self.session = session

    async def create(
        self,
        order_create: OrderCreate,
        owner_id: uuid.UUID,
        email_id: uuid.UUID | None = None,
    ) -> Order:

        if order_create.base_document is None:
            raise ValueError("Base document cannot be None")
        if order_create.base_document_name is None:
            raise ValueError("Base document name cannot be None")

        # Get from external service
        user = self.user_service.get_by_id(owner_id)

        # Process parsing
        user, order_create = await process(
            order_create=order_create,
            ai_service=self.ai_service,
            user=user,
        )

        # Adapt the ids
        update = {"owner_id": user.id, "email_id": email_id}
        order = Order.model_validate(order_create, update=update)

        # Timestamp
        order.state_set_at = {
            OrderState.PENDING.value: datetime.now(timezone.utc).isoformat()
        }

        # Create the order
        self.repository.create(order)

        # Approve the order (if needed)
        if user and user.is_auto_approved:
            order = self.approve(order_update=OrderUpdate(), id=order.id, user=user)

        return order

    def update(self, order_update: OrderUpdate, id: uuid.UUID) -> Order:
        order = self.get_by_id(id)
        return self.repository.update(
            order, update=order_update.model_dump(exclude_unset=True)
        )

    def adapt_state(
        self, order_update: OrderUpdate, new_state: OrderState
    ) -> OrderUpdate:

        current_time = datetime.now(timezone.utc).isoformat()

        # Initialize state_set_at if it doesn't exist
        if order_update.state_set_at is None:
            order_update.state_set_at = {}

        # Update the state timestamps using enum value
        order_update.state_set_at[new_state.value] = current_time

        # Update the order state
        order_update.state = new_state

        return order_update

    def approve(self, order_update: OrderUpdate, id: uuid.UUID, user: User) -> Order:

        from app.services._orders._postprocessors_orders import _postprocess_order

        state = _postprocess_order(user)

        # Adaptations
        order_update = self.adapt_state(order_update, state)

        return self.update(order_update, id)

    def get_all(self, skip: int, limit: int, owner_id: uuid.UUID) -> list[Order]:
        return self.repository.get_all_by_kwargs(
            skip=skip,
            limit=limit,
            **{"owner_id": owner_id},
        )

    def get_by_id(self, id: uuid.UUID) -> Order:
        order = self.repository.get_by_id(id)
        if order is None:
            raise ValueError("Order not found")
        return order

    def get_count(self, owner_id: uuid.UUID) -> int:
        return self.repository.count_by_kwargs(**{"owner_id": owner_id})

    def delete(self, id: uuid.UUID) -> None:
        self.repository.delete(id)
