import base64
import io
import json
import uuid
from typing import Any

import pdfplumber
from app.api.deps import CurrentAIClient, CurrentUser, SessionDep
from app.models import (
    Message,
    Order,
    OrderCreate,
    OrderPublic,
    OrdersPublic,
    OrderUpdate,
)
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=OrdersPublic)
def read_orders(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve orders.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Order)
        count = session.exec(count_statement).one()
        statement = select(Order).offset(skip).limit(limit)
        orders = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Order)
            .where(Order.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Order)
            .where(Order.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        orders = session.exec(statement).all()

    return OrdersPublic(data=orders, count=count)


@router.get("/{id}", response_model=OrderPublic)
def read_order(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get order by ID.
    """
    order = session.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if not current_user.is_superuser and (order.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Permisos insuficientes")
    return order


@router.post("/", response_model=OrderPublic)
def create_and_process_order(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_ai_client: CurrentAIClient,
    order_in: OrderCreate,
) -> Any:
    """
    Create and Process new order.
    """
    order = Order.model_validate(order_in, update={"owner_id": current_user.id})

    # Process order name
    def in_name_2_out_name(name: str) -> str:
        name, _ = name.rsplit(".", 1)
        return f"{name}_ammonit_output.csv"

    order.out_document_name = in_name_2_out_name(order.in_document_name)

    # Read document text
    if order.in_document is None:
        raise HTTPException(
            status_code=400, detail="Documento de entrada no puede ser None"
        )
    with pdfplumber.open(io.BytesIO(order.in_document)) as f:
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
        price_per_unit: str = Field(..., description="The price per unit of the item")

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
            ..., description="Total ammount of energy consumed for current bill, in kWh"
        )

    # Clasiffy document
    if (
        "iberdrola" in in_document_text.lower()
        or "curenergía" in in_document_text.lower()
    ):
        base_model = EnergyBill
    elif "invoice" in in_document_text.lower():
        base_model = InvoiceData
    else:
        raise HTTPException(
            status_code=400, detail="No se ha podido clasificar el documento"
        )

    # Process document
    completion = current_ai_client.beta.chat.completions.parse(
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
    order.out_document = csv_buffer.getvalue().encode("utf-8")

    # Save order in db
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.delete("/{id}")
def delete_order(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an order.
    """
    order = session.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if not current_user.is_superuser and (order.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Permisos insuficientes")
    session.delete(order)
    session.commit()
    return Message(message="Pedido eliminado correctamente")
