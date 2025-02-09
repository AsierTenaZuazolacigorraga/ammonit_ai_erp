import base64
import io
import json
import uuid

import pdfplumber
from app.models import Order, OrderCreate
from app.repositories.orders import OrderRepository
from openai import OpenAI


class OrderService:
    def __init__(
        self,
        repository: OrderRepository,
        ai_client: OpenAI,
    ) -> None:
        self.repository = repository
        self.ai_client = ai_client

    def create(self, *, order_create: OrderCreate, owner_id: uuid.UUID) -> Order:
        db_obj = Order.model_validate(order_create, update={"owner_id": owner_id})

        # Process order name
        def in_name_2_out_name(name: str) -> str:
            name, _ = name.rsplit(".", 1)
            return f"{name}_ammonit_output.csv"

        db_obj.out_document_name = in_name_2_out_name(db_obj.in_document_name)

        # Read document text
        with pdfplumber.open(io.BytesIO(db_obj.in_document)) as f:
            in_document_text = ""
            for page in f.pages:
                in_document_text += page.extract_text()

        # Define basemodels
        from io import BytesIO, StringIO
        from typing import List

        import pandas as pd
        from pydantic import BaseModel, Field

        class InvoiceItem(BaseModel):
            name: str = Field(..., description="The name of the item")
            quantity: int = Field(..., description="The quantity of the item")
            price_per_unit: str = Field(
                ..., description="The price per unit of the item"
            )

        class InvoiceData(BaseModel):
            invoice_number: str = Field(
                ..., description="The unique identifier of the invoice"
            )
            date: str = Field(
                ..., description="The date of the invoice, formatted as YYYY-MM-DD"
            )
            vendor_details: str = Field(
                ..., description="Details about the vendor, including name and address"
            )
            invoice_total: str = Field(
                ..., description="The total amount for the invoice, including taxes"
            )
            items: List[InvoiceItem] = Field(
                ..., description="List of items in the invoice"
            )

        class EnergyBill(BaseModel):
            account_number: str = Field(..., description="Account number")
            total_energy_consumption: float = Field(
                ...,
                description="Total ammount of energy consumed for current bill, in kWh",
            )

        # Clasiffy document
        if (
            "iberdrola" in in_document_text.lower()
            or "curenergía" in in_document_text.lower()
        ):
            base_model = EnergyBill
        elif "invoice" in in_document_text.lower():
            base_model = InvoiceData

        # Process document
        completion = self.ai_client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"""
        Extract the following information from the invoice:
        {json.dumps(base_model.model_json_schema(), indent=2)}
        Text: {in_document_text}""",
                },
            ],
            response_format=base_model,
        )
        base_parsed = completion.choices[0].message.parsed

        # Convert the list of dictionaries into a DataFrame
        df = pd.DataFrame(base_parsed)

        # Export the DataFrame to CSV in binary format
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, sep=";", index=False)
        db_obj.out_document = csv_buffer.getvalue().encode("utf-8")

        return self.repository.create(db_obj)
