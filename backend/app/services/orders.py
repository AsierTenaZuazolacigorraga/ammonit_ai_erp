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
from app.models import Client, Order, OrderCreate, OrderState, OrderUpdate
from app.repositories.base import CRUDRepository
from app.services.bridges import BridgeService
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


async def parse_pdf_binary_2_md(
    ai_client: OpenAI, pdf_binary: bytes, pdf_name: str
) -> str:
    # Preprocess PDF to remove irrelevant pages
    filtered_pdf_binary = preprocess_pdf(pdf_binary)

    # Convert to md
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
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{parse_pdf_binary_2_base64_jpg(pdf_binary)}",
                    }
                ],
                # "content": [
                #     {
                #         "type": "input_file",
                #         "filename": pdf_name,
                #         "file_data": f"data:application/pdf;base64,{parse_pdf_binary_2_base64(pdf_binary)}",
                #     }
                # ],
            },  # type: ignore
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


def preprocess_pdf(pdf_binary: bytes) -> bytes:
    # Keywords that indicate the start of irrelevant content
    irrelevant_keywords = [
        'Conditions Générales d\'Achat entre MATISA Matériel Industriel SA ("Matisa") et ses Fournisseurs ("Fournisseur")',
    ]

    # Create a new PDF writer
    pdf_writer = PyPDF2.PdfWriter()

    # Read the PDF from binary data
    pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_binary))

    # Process each page until we find irrelevant content
    for i in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[i]
        text = page.extract_text().lower()

        # Check if page contains irrelevant content
        if any(keyword.lower() in text for keyword in irrelevant_keywords):
            # Stop processing once we find irrelevant content
            break

        # Add relevant page to the new PDF
        pdf_writer.add_page(page)

    # If we filtered out all pages, keep at least the first page
    if len(pdf_writer.pages) == 0 and len(pdf_reader.pages) > 0:
        pdf_writer.add_page(pdf_reader.pages[0])

    # Instead of saving to a file, write to a BytesIO object
    output_buffer = BytesIO()
    pdf_writer.write(output_buffer)

    # Get the binary data from the buffer
    output_buffer.seek(0)
    return output_buffer.getvalue()


def parse_md_2_order(
    ai_client: OpenAI, md: str, clients: list[Client]
) -> tuple[dict, Client]:

    clients_clasification = ",\n".join(
        f'"- {client.name}: {client.clasifier}"' for client in clients
    )

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
    response = ai_client.responses.create(
        model="gpt-4.1-nano",
        input=[
            {
                "role": "system",
                "content": "Extract the order information",
            },
            {"role": "user", "content": md},
        ],
        text=json.loads(client.structure),
        reasoning={},
        tools=[],
        temperature=0,
        max_output_tokens=2048,
        top_p=0,
        store=True,
    )

    if response.output_text is None:
        raise ValueError("Failed to parse the order information from the markdown.")

    return json.loads(response.output_text), client


def parse_order_2_csv(order: dict) -> str:

    # Find keys that contain lists of dictionaries
    list_keys = []
    for key, value in order.items():
        if isinstance(value, list) and value and isinstance(value[0], dict):
            list_keys.append(key)

    # If we found any keys with lists of dictionaries
    if list_keys:
        # Create a list to hold all rows
        rows = []

        # Extract common fields from the order (non-list fields)
        common_fields = {k: v for k, v in order.items() if k not in list_keys}

        # For each list key, process its items
        for list_key in list_keys:
            for item in order[list_key]:
                row = common_fields.copy()
                row.update(item)
                rows.append(row)

        # Create DataFrame from the rows
        df = pd.DataFrame(rows)

    # If the order doesn't have any list keys, convert it directly
    else:
        # For a flat dictionary, convert to a single-row DataFrame
        df = pd.DataFrame([order])

    return df.to_csv(sep=";", index=False)


class OrderService:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.repository = CRUDRepository[Order](Order, session)
        self.clients_service = ClientService(session)
        self.users_service = UserService(session)
        self.bridge_service = BridgeService(session)
        self.session = session

        # Initialize clients
        self.ai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def create(self, *, order_create: OrderCreate, owner_id: uuid.UUID) -> Order:

        # Get from external service
        clients = self.clients_service.get_all(skip=0, limit=100, owner_id=owner_id)
        user = self.users_service.get_by_id(owner_id)

        # Process parsing
        if order_create.base_document is None:
            raise ValueError("Base document cannot be None")
        if order_create.base_document_name is None:
            raise ValueError("Base document name cannot be None")
        md = await parse_pdf_binary_2_md(
            self.ai_client, order_create.base_document, order_create.base_document_name
        )

        # Use the new parse_md_2_order function with ai_client
        order_dict, client = parse_md_2_order(self.ai_client, md, clients)

        # Creat the order
        order = Order.model_validate(order_create, update={"owner_id": client.id})
        order.content_processed = parse_order_2_csv(order_dict)
        self.repository.create(order)

        # Approve the order (if needed)
        if user and user.is_auto_approved:
            order = await self.approve(order_update=OrderUpdate(), id=order.id)

        return order

    async def approve(self, order_update: OrderUpdate, id: uuid.UUID) -> Order:
        order = self.get_by_id(id)
        if not order:
            raise ValueError("Order not found")

        # Update the order
        order_update.approved_at = datetime.now(timezone.utc)

        # Integrate in ERP
        order_update = self.bridge_service.execute(order_update=order_update)

        return self.repository.update(
            order, update=order_update.model_dump(exclude_unset=True)
        )

    def get_all(self, skip: int, limit: int, owner_id: uuid.UUID) -> list[Order]:
        clients = self.clients_service.get_all(
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

    def get_by_id(self, id: uuid.UUID) -> Order | None:
        return self.repository.get_by_id(id)

    def get_count(self, owner_id: uuid.UUID) -> int:
        clients = self.clients_service.get_all(
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
