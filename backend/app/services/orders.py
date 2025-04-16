import base64
import io
import json
import os
import pprint
import tempfile
import uuid
from io import BytesIO, StringIO
from typing import List, Union

import pandas as pd
import PyPDF2
from app.models import Client, Order, OrderCreate
from app.repositories.orders import OrderRepository
from app.services.clients import ClientService
from dotenv import load_dotenv
from fastapi import HTTPException
from groq import Groq
from llama_parse import LlamaParse, ResultType
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()


def in_name_2_out_name(name: str) -> str:
    name, _ = name.rsplit(".", 1)
    return f"{name}_ammonit_output.csv"


def parse_pdf_binary_2_md(pdf_binary: bytes) -> str:
    # Preprocess PDF to remove irrelevant pages
    filtered_pdf_binary = _preprocess_pdf(pdf_binary)

    # Create a temporary file for the filtered PDF
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as f:
        f.write(filtered_pdf_binary)
        f.flush()

        pdf_reader = PyPDF2.PdfReader(f.name)
        if len(pdf_reader.pages) > 8:
            raise HTTPException(
                status_code=500,
                detail="El archivo PDF excede el límite máximo permitido de 8 páginas.",
            )

        # Add a check to ensure the API key is not None
        api_key = os.getenv("LLAMACLOUD_API_KEY")
        if api_key is None:
            raise ValueError("LLAMACLOUD_API_KEY environment variable is not set")

        parser = LlamaParse(
            api_key=api_key,
            result_type=ResultType.MD,
            premium_mode=True,
            do_not_cache=True,
            invalidate_cache=True,
        )

        documents = parser.load_data(f.name)
        md = ""
        for document in documents:
            md = md + document.text

    return md


def _preprocess_pdf(pdf_binary: bytes) -> bytes:
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
    md: str, ai_client: OpenAI, groq_client: Groq, clients: list[Client]
) -> dict:

    # Extract client
    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": f"""
Which client does this order come from? Select from the following list. Only respond with the client name as is specified in the list.
If you cannot identify the client, respond with "unknown":
[
{", ".join(f'"{client.name}"' for client in clients)}
]
""",
            },
            {"role": "user", "content": md},
        ],
    )
    client = completion.choices[0].message.content
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
        model="gpt-4o-mini",
        input=[
            {
                "role": "system",
                "content": "Extract the order information",
            },
            {"role": "user", "content": md},
        ],
        text=json.loads(client.structure),
    )

    if response.output_text is None:
        raise ValueError("Failed to parse the order information from the markdown.")

    return json.loads(response.output_text)


class OrderService:
    def __init__(
        self,
        repository: OrderRepository,
        clients_service: ClientService,
        ai_client: OpenAI,
        groq_client: Groq,
    ) -> None:
        self.repository = repository
        self.clients_service = clients_service
        self.ai_client = ai_client
        self.groq_client = groq_client

    def create(self, *, order_create: OrderCreate, owner_id: uuid.UUID) -> Order:
        db_obj = self.process(order_create, owner_id)
        return self.repository.create(db_obj)

    def process(self, order_create: OrderCreate, owner_id: uuid.UUID) -> Order:
        db_obj = Order.model_validate(order_create, update={"owner_id": owner_id})

        # Process order name
        if db_obj.in_document_name is None:
            raise ValueError("Input document name cannot be None")
        db_obj.out_document_name = in_name_2_out_name(db_obj.in_document_name)

        # Process parsing
        if db_obj.in_document is None:
            raise ValueError("Input document cannot be None")
        md = parse_pdf_binary_2_md(db_obj.in_document)

        # Get all possible clients
        clients = self.clients_service.get_all_by_owner_id(owner_id=owner_id)

        # Use the new parse_md_2_order function with ai_client
        order = parse_md_2_order(md, self.ai_client, self.groq_client, clients)

        # Convert into a DataFrame
        data = []
        for item in order["items"]:
            data.append(
                {
                    "Número de Pedido": order["number"],
                    "Código": item["code"],
                    "Descripción": item["description"],
                    "Cantidad": item["quantity"],
                    "Precio Unitario": item["unit_price"],
                    "Plazo": item["deadline"],
                }
            )
        df = pd.DataFrame(data)

        # Export the DataFrame to CSV in binary format
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, sep=";", index=False)
        db_obj.out_document = csv_buffer.getvalue().encode("utf-8")

        return db_obj
