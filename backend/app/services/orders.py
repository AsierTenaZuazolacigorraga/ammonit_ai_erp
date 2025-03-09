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
from app.models import Order, OrderCreate
from app.repositories.orders import OrderRepository
from dotenv import load_dotenv
from groq import Groq
from llama_parse import LlamaParse, ResultType
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

GENERIC_NUMBER_DESC = "The number of the order"
GENERIC_ITEMS_DESC = "The items in the order"
GENERIC_CODE_DESC = "The code of the item"
GENERIC_DESCRIPTION_DESC = "The description of the item"
GENERIC_QUANTITY_DESC = "The quantity of items to order"
GENERIC_UNIT_PRICE_DESC = "The unit price of the item"
GENERIC_DEADLINE_DESC = "The deadline or due date for the item"


class ItemDanobat(BaseModel):
    code: str = Field(
        ...,
        description=f"{GENERIC_CODE_DESC}",
    )
    description: str = Field(
        ...,
        description=f"{GENERIC_DESCRIPTION_DESC}",
    )
    quantity: int = Field(
        ...,
        description=f"{GENERIC_QUANTITY_DESC}",
    )
    unit_price: float = Field(..., description=f"{GENERIC_UNIT_PRICE_DESC}")
    deadline: str = Field(
        ...,
        description=f"{GENERIC_DEADLINE_DESC}",
    )


class OrderDanobat(BaseModel):
    number: str = Field(
        ...,
        description=f"{GENERIC_NUMBER_DESC}",
    )
    items: List[ItemDanobat] = Field(
        ...,
        description=f"{GENERIC_ITEMS_DESC}",
    )


class ItemFagor(BaseModel):
    code: str = Field(
        ..., description=f"{GENERIC_CODE_DESC}. The code is usually repeated two times."
    )
    description: str = Field(
        ...,
        description=f"{GENERIC_DESCRIPTION_DESC}",
    )
    quantity: int = Field(
        ...,
        description=f"{GENERIC_QUANTITY_DESC}",
    )
    unit_price: float = Field(
        ...,
        description=f"{GENERIC_UNIT_PRICE_DESC}. Be careful, report only the unit price (sometimes are provided both the unit price and the total price).",
    )
    deadline: str = Field(
        ...,
        description=f"{GENERIC_DEADLINE_DESC}",
    )


class OrderFagor(BaseModel):
    number: str = Field(
        ...,
        description=f"{GENERIC_NUMBER_DESC}. Usually is provided as 'Eskari'.",
    )
    items: List[ItemFagor] = Field(
        ...,
        description=f"{GENERIC_ITEMS_DESC}",
    )


class ItemInola(BaseModel):
    code: str = Field(..., description=f"{GENERIC_CODE_DESC}")
    description: str = Field(..., description=f"{GENERIC_DESCRIPTION_DESC}")
    quantity: int = Field(..., description=f"{GENERIC_QUANTITY_DESC}")
    unit_price: float = Field(..., description=f"{GENERIC_UNIT_PRICE_DESC}")
    deadline: str = Field(
        ...,
        description=f"{GENERIC_DEADLINE_DESC}. Usually the deadline is provided for the entire order (as F.ENTREGA) rather than for each item independently",
    )


class OrderInola(BaseModel):
    number: str = Field(..., description=f"{GENERIC_NUMBER_DESC}")
    items: List[ItemInola] = Field(..., description=f"{GENERIC_ITEMS_DESC}")


class ItemMatisa(BaseModel):
    code: str = Field(
        ...,
        description=f"{GENERIC_CODE_DESC}. Usually provided as 'Référence article et désignation'. The code is provided in digits in this format: XX-XX-XXX-XXXXX.",
    )
    description: str = Field(
        ...,
        description=f"{GENERIC_DESCRIPTION_DESC}. Usually provided as 'Référence article et désignation'. Consider description all but the code.",
    )
    quantity: int = Field(..., description=f"{GENERIC_QUANTITY_DESC}")
    unit_price: float = Field(..., description=f"{GENERIC_UNIT_PRICE_DESC}")
    deadline: str = Field(..., description=f"{GENERIC_DEADLINE_DESC}")


class OrderMatisa(BaseModel):
    number: str = Field(
        ...,
        description=f"{GENERIC_NUMBER_DESC}. Usually provided as 'COMMANDE ACHAT'.",
    )
    items: List[ItemMatisa] = Field(..., description=f"{GENERIC_ITEMS_DESC}")


class ItemUlma(BaseModel):
    code: str = Field(
        ..., description=f"{GENERIC_CODE_DESC}. Usually provided as 'Proyecto Código'."
    )
    description: str = Field(..., description=f"{GENERIC_DESCRIPTION_DESC}")
    quantity: int = Field(..., description=f"{GENERIC_QUANTITY_DESC}")
    unit_price: float = Field(
        ...,
        description=f"{GENERIC_UNIT_PRICE_DESC}. Usually provided as 'Precio'.",
    )
    deadline: str = Field(
        ...,
        description=f"{GENERIC_DEADLINE_DESC}. Usually provided as 'Entrega'.",
    )


class OrderUlma(BaseModel):
    number: str = Field(
        ...,
        description=f"{GENERIC_NUMBER_DESC}. Usually provided in a table called 'Pedido de compra', in the field names as 'Num.'.",
    )
    items: List[ItemUlma] = Field(..., description=f"{GENERIC_ITEMS_DESC}")


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
    md: str, ai_client: OpenAI, groq_client: Groq
) -> Union[OrderDanobat, OrderFagor, OrderInola, OrderMatisa, OrderUlma]:
    # Extract client
    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """
Which client does this order come from? Select from the following list and only respond with the client name as is specified in the list:
[
"danobat",
"fagor",
"inola",
"matisa",
"ulma"
]
""",
            },
            {"role": "user", "content": md},
        ],
    )
    client = completion.choices[0].message.content
    if client is None:
        raise ValueError("Failed to extract the client from the order.")

    # Decide the model
    client = client.lower()
    match client:
        case "danobat":
            base_model = OrderDanobat
        case "fagor":
            base_model = OrderFagor
        case "inola":
            base_model = OrderInola
        case "matisa":
            base_model = OrderMatisa
        case "ulma":
            base_model = OrderUlma
        case _:
            raise ValueError(f"Unknown client: {client}")

    # Extract info
    completion = ai_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Extract the order information",
            },
            {"role": "user", "content": md},
        ],
        response_format=base_model,
    )
    order = completion.choices[0].message.parsed
    if order is None:
        raise ValueError("Failed to parse the order information from the markdown.")

    return order


class OrderService:
    def __init__(
        self,
        repository: OrderRepository,
        ai_client: OpenAI,
        groq_client: Groq,
    ) -> None:
        self.repository = repository
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

        # Use the new parse_md_2_order function with ai_client
        order = parse_md_2_order(md, self.ai_client, self.groq_client)

        # Convert into a DataFrame
        data = []
        for item in order.items:
            data.append(
                {
                    "Número de Pedido": order.number,
                    "Código": item.code,
                    "Descripción": item.description,
                    "Cantidad": item.quantity,
                    "Precio Unitario": item.unit_price,
                    "Plazo": item.deadline,
                }
            )
        df = pd.DataFrame(data)

        # Export the DataFrame to CSV in binary format
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, sep=";", index=False)
        db_obj.out_document = csv_buffer.getvalue().encode("utf-8")

        return db_obj
