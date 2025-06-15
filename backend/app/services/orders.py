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
    ai_client: OpenAI, document: bytes, document_name: str, user: User
) -> str:

    # Convert to md
    if not document_name.endswith(".pdf"):
        raise ValueError(f"Unsupported file type: {document_name}")

    from app.services._orders._prompts import DOCUMENT_2_MD_PROMPT

    response = ai_client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "developer",
                "content": [
                    {
                        "type": "input_text",
                        "text": DOCUMENT_2_MD_PROMPT,
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{parse_pdf_binary_2_base64_jpg(document)}",
                    }
                ],
            },  # type: ignore
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[],
        temperature=0,
        max_output_tokens=2048,
        top_p=0,
        store=True,
        metadata={
            "service": "orders",
            "query": "document_2_md",
            "user_id": str(user.id),
            "user_email": user.email,
        },
    )
    md = response.output_text
    if md is None:
        raise ValueError("Failed to parse the PDF to markdown.")
    return md


async def parse_md_2_order(ai_client: OpenAI, md: str, user: User) -> dict:

    from app.services._orders._prompts import MD_2_ORDER_PROMPT

    response = ai_client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "developer",
                "content": [
                    {
                        "type": "input_text",
                        "text": MD_2_ORDER_PROMPT.replace(
                            "{ADDITIONAL_RULES}",
                            user.orders_additional_rules or "",
                        ).replace(
                            "{PARTICULAR_RULES}",
                            user.orders_particular_rules or "",
                        ),
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": md,
                    }
                ],
            },
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[],
        temperature=0,
        max_output_tokens=2048,
        top_p=0,
        store=True,
        metadata={
            "service": "orders",
            "query": "md_2_order",
            "user_id": str(user.id),
            "user_email": user.email,
        },
    )
    order = response.output_text
    if order is None:
        raise ValueError("Failed to parse the markdown to order.")

    from app.services._orders._prompts import ORDER_SCHEMA

    # Extract structured info
    response = ai_client.responses.create(
        model="gpt-4.1-nano",
        input=[
            {
                "role": "developer",
                "content": f"""
El usuario te proporcionará un texto con cierto formato json.
Tu tarea es analizar el texto y responder con un json estructurado acorde a esta especificación:

{json.dumps(ORDER_SCHEMA, indent=4, ensure_ascii=False)}
""",
            },
            {
                "role": "user",
                "content": order,
            },
        ],
        text={"format": {"type": "json_schema", **ORDER_SCHEMA}},  # type: ignore
        reasoning={},
        tools=[],
        temperature=0,
        max_output_tokens=2048,
        top_p=0,
        store=True,
        metadata={
            "service": "orders",
            "query": "order_2_dict",
            "user_id": str(user.id),
            "user_email": user.email,
        },
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
    order_create: OrderCreate, ai_client: OpenAI, user: User
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
        ai_client, document, order_create.base_document_name, user
    )

    # Parse md to order
    order_dict = await parse_md_2_order(ai_client, md, user)

    # Preprocess order
    order_create.content_processed = preprocess_order(order_dict, user)
    order_create.content_structured = order_dict
    order_create.base_document_markdown = md

    return user, order_create


def preprocess_document(document: bytes, document_name: str, user: User) -> bytes:
    from app.services._orders._preprocessors_documents import _preprocess_document

    return _preprocess_document(document, document_name, user)


def preprocess_order(order_dict: dict, user: User) -> str:
    from app.services._orders._preprocessors_orders import _preprocess_order

    return parse_order_dict_2_csv(_preprocess_order(order_dict, user))


class OrderService:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.repository = CRUDRepository[Order](Order, session)
        self.user_service = UserService(session)
        self.session = session

        # Initialize clients
        self.ai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def create(
        self,
        *,
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
            ai_client=self.ai_client,
            user=user,
        )

        # Adapt the ids
        update = {"owner_id": user.id, "email_id": email_id}
        order = Order.model_validate(order_create, update=update)

        # Create the order
        self.repository.create(order)

        # Approve the order (if needed)
        if user and user.is_auto_approved:
            order = self.approve(order_update=OrderUpdate(), id=order.id, user=user)

        return order

    def approve(self, order_update: OrderUpdate, id: uuid.UUID, user: User) -> Order:

        order = self.get_by_id(id)

        # Update the order
        order_update.approved_at = datetime.now(timezone.utc)

        from app.services._orders._postprocessors_orders import _postprocess_order

        state, created_in_erp_at = _postprocess_order(user)
        order_update.state = state
        order_update.created_in_erp_at = created_in_erp_at

        return self.repository.update(
            order, update=order_update.model_dump(exclude_unset=True)
        )

    def update_erp_state(
        self, order_update: OrderUpdate, id: uuid.UUID, user: User
    ) -> Order:

        order = self.get_by_id(id)

        # Update the order
        order_update.created_in_erp_at = datetime.now(timezone.utc)
        return self.repository.update(
            order, update=order_update.model_dump(exclude_unset=True)
        )

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
