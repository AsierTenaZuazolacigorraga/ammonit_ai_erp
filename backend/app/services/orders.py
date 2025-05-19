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
from app.models import Client, Email, Order, OrderCreate, OrderState, OrderUpdate, User
from app.repositories.base import CRUDRepository
from app.services.clients import ClientService
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
    ai_client: OpenAI, document: bytes, document_name: str
) -> str:

    # Convert to md
    if document_name.endswith(".pdf"):
        user_prompt = {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{parse_pdf_binary_2_base64_jpg(document)}",
                }
            ],
            # "content": [
            #     {
            #         "type": "input_file",
            #         "filename": pdf_name,
            #         "file_data": f"data:application/pdf;base64,{parse_pdf_binary_2_base64(pdf_binary)}",
            #     }
            # ],
        }
    elif document_name.endswith(".txt"):
        user_prompt = {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": document,
                }
            ],
        }
    else:
        raise ValueError(f"Unsupported file type: {document_name}")
    response = ai_client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": """
1. Read the document you are provided
2. Understand the text structure and display of the different contents
3. Convert the document into markdown text, making sure to keep the same text structure and display
4. Respond just with the markdown text, using the same language used in the document
""",
                    }
                ],
            },
            user_prompt,  # type: ignore
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[],
        temperature=0,
        max_output_tokens=2048,
        top_p=0,
        store=True,
    )

    md = response.output_text
    if md is None:
        raise ValueError("Failed to parse the PDF to markdown.")
    return md


async def parse_md_2_order(
    ai_client: OpenAI,
    md: str,
    clients: list[Client],
) -> tuple[BaseModel, Client]:

    # Extract client
    response = ai_client.responses.create(
        model="gpt-4.1-nano",
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"""
Which client does this order come from? Select from the following list. Only respond with the client name as is specified in the list.
If you cannot identify the client, respond with "unknown":
[
{clients_clasification}
]
""",
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
    )
    client = response.output_text
    if client is None:
        raise ValueError("Failed to extract the client info from the order.")

    # Decide the model
    client = client.lower()
    possible_clients = [c for c in clients if c.name.lower() == client]
    if len(possible_clients) == 0:
        raise ValueError(f"Unknown client: {client}")
    if len(possible_clients) > 1:
        raise ValueError(f"Multiple clients found for {client}: {possible_clients}")
    client = possible_clients[0]

    # Extract info
    response = ai_client.responses.parse(
        model="gpt-4.1-nano",
        input=[
            {
                "role": "system",
                "content": "Extract the order information",
            },
            {"role": "user", "content": md},
        ],
        text_format=client_structure,
        reasoning={},
        tools=[],
        temperature=0,
        max_output_tokens=2048,
        top_p=0,
        store=True,
    )

    if response.output_parsed is None:
        raise ValueError("Failed to parse the order information from the markdown.")

    return response.output_parsed, client


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
    order_create: OrderCreate,
    ai_client: OpenAI,
    clients: list[Client],
    user: User,
) -> tuple[User, Client, Order]:

    if order_create.base_document is None:
        raise ValueError("Base document cannot be None")
    if order_create.base_document_name is None:
        raise ValueError("Base document name cannot be None")

    # Preprocess document
    document = preprocess_document(
        order_create.base_document, order_create.base_document_name, user
    )

    # Parse document to md
    md = await parse_document_2_md(ai_client, document, order_create.base_document_name)

    # Parse md to order
    order_basemodel, client = await parse_md_2_order(ai_client, md, clients)

    # Preprocess order
    order_create.content_processed = preprocess_order(
        order_basemodel,
        user,
    )

    # Create the order
    order = Order.model_validate(order_create)

    return user, client, order


def preprocess_document(document: bytes, document_name: str, user: User) -> bytes:
    from app.services._orders._preprocessors_documents import _preprocess_document

    return _preprocess_document(document, document_name, user)


def preprocess_order(
    order_basemodel: BaseModel,
    user: User,
) -> str:

    from app.services._orders._preprocessors_orders import _preprocess_order

    return parse_order_dict_2_csv(_preprocess_order(order_basemodel, user))


class OrderService:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.repository = CRUDRepository[Order](Order, session)
        self.client_service = ClientService(session)
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
        clients = self.client_service.get_all(skip=0, limit=100, owner_id=owner_id)
        user = self.user_service.get_by_id(owner_id)

        # Process parsing
        user, client, order = await process(
            order_create=order_create,
            ai_client=self.ai_client,
            clients=clients,
            user=user,
        )

        # Adapt the ids
        order.owner_id = client.id
        if email_id is not None:
            order.email_id = email_id

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
        clients = self.client_service.get_all(
            skip=0,
            limit=100,
            owner_id=owner_id,
        )
        if not clients:
            return []
        client_ids = [client.id for client in clients]
        return self.repository.get_all_by_kwargs(
            skip=skip,
            limit=limit,
            **{"owner_id": client_ids},
        )

    def get_by_id(self, id: uuid.UUID) -> Order:
        order = self.repository.get_by_id(id)
        if order is None:
            raise ValueError("Order not found")
        return order

    def get_count(self, owner_id: uuid.UUID) -> int:
        clients = self.client_service.get_all(
            skip=0,
            limit=100,
            owner_id=owner_id,
        )
        if not clients:
            return 0
        client_ids = [client.id for client in clients]
        return self.repository.count_by_kwargs(**{"owner_id": client_ids})

    def delete(self, id: uuid.UUID) -> None:
        self.repository.delete(id)
