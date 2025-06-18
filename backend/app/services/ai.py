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
from app.models import (
    Email,
    Order,
    OrderCreate,
    OrderState,
    OrderUpdate,
    PromptBase,
    User,
)
from app.repositories.base import CRUDRepository
from app.services.users import UserService
from dotenv import load_dotenv
from fastapi import HTTPException
from groq import Groq
from llama_parse import LlamaParse, ResultType
from openai import OpenAI
from openai.types.responses import Response
from pdf2image import convert_from_bytes
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlmodel import Session

load_dotenv()

logger = get_logger(__name__)


document_2_md = PromptBase(
    query="document_2_md",
    service="orders",
    model="gpt-4.1-mini",
    prompt="""
1. Lee el documento que se te proporciona
2. Comprende la estructura del texto y la visualización de los diferentes contenidos
3. Convierte el documento a texto markdown, asegurándote de mantener la misma estructura y visualización del texto
4. Responde solo con el texto markdown, usando el mismo idioma que se usa en el documento

Notas:
- Si el documento contiene imágenes, transcríbelas e inclúyelas en el texto markdown
- Si las imágenes contienen texto, incluye el texto en el texto markdown
""",
    structure=None,
    version=1,
)

md_2_order = PromptBase(
    query="md_2_order",
    service="orders",
    model="gpt-4.1-mini",
    prompt="""
# Objetivo

Eres un asistente especializado en extraer información estructurada de pedidos en formato markdown. Tu tarea es, dada la transcripción en markdown de un documento de pedido
(que puede variar en formato, contenido,columnas, distribución o idioma), identificar y normalizar los siguientes datos:

- order_number: Número de pedido, identificador único que se usa para identificar el pedido
- client: Nombre de la empresa cliente
- general_delivery_date: Fecha de entrega global si existe
- items: Lista de objetos con, para cada uno:
   - code: Código de item
   - description: Nombre o descripción completa (concatenar líneas si la descripción ocupa varias filas)
   - quantity: Cantidad solicitada (entero o decimal según corresponda)
   - unit: Unidad de medida (pcs, unidades, etc.)
   - price: Precio unitario, como número decimal
   - currency: Moneda, si se detecta (por ejemplo "EUR" o "€"), por defecto "EUR"
   - delivery_date: Fecha de entrega específica: si no aparece, usar general_delivery_date

# Reglas de extracción y normalización

- Fechas:
  - Reconoce formatos comunes (dd/mm/yyyy, d/m/yy, yyyy-mm-dd, etc.) y normalizar a ISO 8601 ("YYYY-MM-DD")
  - Si hay varias fechas generales (p.ej. "FECHA: 25/02/2025" y "Lugar de entrega" con fecha distinta), identifica la fecha que se refiere a la entrega global, y descarta otras posibles fechas como fecha de emisión
  - Si falta delivery_date en un ítem, asigna el valor de general_delivery_date. Si no hay general_delivery_date, delivery_date en items puede quedar null
  - Si falta general_delivery_date, general_delivery_date puede quedar null
- Precios:
  - Extrae número decimal (reemplazar coma decimal si hace falta)
  - Detecta símbolo de moneda (€ u otros) y mapear a código ISO si es posible. Separar price y currency. Si no se detecta moneda, se asume EUR.
- Cantidades:
  - Normaliza quantity como número (entero o decimal) y unidad aparte.
  - Si no se detecta unidad, inferirla a partir de la descripción del item (la unidad no puede ser null). Si no se puede inferir, establece unidad como "unidades"
- Cliente:
  - Entiende como cliente, la empresa emisora del pedido. La empresa receptora del pedido, es la empresa para la que tu trabajas
  - El cliente simpre será distinto a la empresa para la que tu trabajas
  - El nombre de cliente, ha de ser un nombre asociado a una empresa, y no a un nombre de una persona particular o un trabajador que aparezca en el documento
- Detecta etiquetas con tolerancia: p.ej. "Nº:", "Número de pedido", "Order No", "Pedido", u otras variaciones. Usa patrones y proximidad semántica
- Tablas markdown: manejar filas que continúan descripción en filas siguientes con celdas vacías en columnas clave. Concatenar texto de descripción con espacios o saltos según convenga
- Columnas variables: nombres de columna pueden variar ("Artículo", "Código", "Referencia", "Descripción", etc.). Usa cercanía semántica:
  - Si una columna parece contener un número largo alfanumérico, puede ser code;
  - Si es texto alfabético extenso, description;
  - Si contiene "€" o patrón de precio, price;
  - Si contiene fecha, delivery_date
- Si no encuentras un campo, establece valor null
- Ignora celdas vacías o de control interno irrelevantes
- Considera posibles idiomas (español, inglés, euskera u otro) en etiquetas de campo: por ejemplo "Entrega", "Delivery", "Entrega prevista", "Entrega-Data" (euskera). Trata de inferir el concepto
{ADDITIONAL_RULES}

# Reglas particulares para algunos clientes
{PARTICULAR_RULES}

# Estructura

Responde solo con un JSON válido que siga esta estructura:

{
  "order_number": string,
  "client": string,
  "general_delivery_date": "YYYY-MM-DD" | null,
  "items": [
    {
      "code": string | null,
      "description": string | null,
      "quantity": number | null,
      "unit": string,
      "price": number | null,
      "currency": string,
      "delivery_date": "YYYY-MM-DD" | null,
    },
    ...
  ]
}
""",
    structure=None,
    version=1,
)

eval = PromptBase(
    query="eval",
    service=None,
    model=None,
    prompt=f"""
La respuesta se considerará como "Fail":
1. Si la respuesta no se proporciona en el formato .json
2. Si el json proporcionado no incluye todos los campos que se solicitan
3. Si, después de que analices profundamente la pregunta y el contexto del usuario, entiendes que cualquiera de los campos de la respuesta:
- Está mal completado, o la información añadida en el campo está incompleta, por cualquier motivo
- Especial atención a los campos que tienen un valor null asociado. Asegúrate de que en el documento original, efectivamente no existe información
  sobre el campo en cuestión y por lo tanto es un null válido

De lo contrario, la respuesta se considerará como "Pass"

Notas:
- Se admite y se entiende que "null" y null son equivalentes
    """,
    structure=None,
    version=1,
)

order_2_json = PromptBase(
    query="order_2_json",
    service="orders",
    model="gpt-4.1-nano",
    prompt="""
El usuario te proporcionará un texto con cierto formato json.
Tu tarea es analizar el texto y responder con un json estructurado acorde a esta especificación:

{structure}
    """,
    structure={
        "name": "order_schema",
        "schema": {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "string",
                    "description": "Número de pedido, identificador único que se usa para identificar el pedido.",
                },
                "client": {
                    "type": "string",
                    "description": "Nombre de la empresa cliente.",
                },
                "general_delivery_date": {
                    "type": "string",
                    "format": "date",
                    "description": "Fecha de entrega global si existe, en formato YYYY-MM-DD.",
                },
                "items": {
                    "type": "array",
                    "description": "Lista de objetos que representan los ítems del pedido.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Código de item. Puede ser null si no existe.",
                            },
                            "description": {
                                "type": "string",
                                "description": "Nombre o descripción completa, concatenando si ocupa varias filas. Puede ser null si no existe.",
                            },
                            "quantity": {
                                "type": "number",
                                "description": "Cantidad solicitada, puede ser entero o decimal. Puede ser null si no existe.",
                            },
                            "unit": {
                                "type": "string",
                                "description": "Unidad de medida (e.g., pcs, unidades, etc.).",
                            },
                            "price": {
                                "type": "number",
                                "description": "Precio unitario como número decimal. Puede ser null si no existe.",
                            },
                            "currency": {
                                "type": "string",
                                "description": "Moneda del precio, e.g. 'EUR' o '€'. Por defecto 'EUR'.",
                            },
                            "delivery_date": {
                                "type": "string",
                                "format": "date",
                                "description": "Fecha de entrega específica. Puede ser null si no existe.",
                            },
                        },
                        "required": [
                            "code",
                            "description",
                            "quantity",
                            "unit",
                            "price",
                            "currency",
                            "delivery_date",
                        ],
                        "additionalProperties": False,
                    },
                },
            },
            "required": [
                "order_number",
                "client",
                "general_delivery_date",
                "items",
            ],
            "additionalProperties": False,
        },
        "strict": False,
    },
    version=1,
)

order_columns_mapping = PromptBase(
    query=None,
    service=None,
    model=None,
    prompt=None,
    structure={
        "order_number": {
            "column": "Número de Pedido",
            "include": True,
        },
        "client": {
            "column": "Cliente",
            "include": False,
        },
        "general_delivery_date": {
            "column": "Fecha de Entrega Global",
            "include": True,
        },
        "code": {
            "column": "Código de Item",
            "include": True,
        },
        "description": {
            "column": "Descripción del Item",
            "include": True,
        },
        "quantity": {
            "column": "Cantidad",
            "include": True,
        },
        "unit": {
            "column": "Unidad",
            "include": True,
        },
        "price": {
            "column": "Precio",
            "include": True,
        },
        "currency": {
            "column": "Moneda",
            "include": True,
        },
        "delivery_date": {
            "column": "Fecha de Entrega",
            "include": True,
        },
    },
    version=1,
)

is_offer_email = PromptBase(
    query="is_offer_email",
    service="emails",
    model="gpt-4.1-nano",
    prompt=f"""
Eres un asistente especializado en analizar correos electrónicos y determinar si son ofertas comerciales.
Por ahora, response siempre con "true".
Solamente responde con con la palabra "true".
""",
    # Please analyze the email data that the user provides and determine if it's an offer-related email.
    # Respond with a single word: 'true' if this appears to be an offer-related email, or 'false' if it's not. Consider factors like:
    # - If it contains pricing information
    # - If it's a proposal or quotation
    # - If it's discussing business terms or conditions
    # - If it's related to sales or business opportunities
    # Respond with only 'true' or 'false'
    # """,
    structure=None,
)

prompts = {
    "document_2_md": document_2_md,
    "md_2_order": md_2_order,
    "eval": eval,
    "order_2_json": order_2_json,
    "order_columns_mapping": order_columns_mapping,
    "is_offer_email": is_offer_email,
}


class AiService:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.ai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def get_prompt(self, prompt_name: str) -> PromptBase:
        return prompts[prompt_name]

    def response_create_basic(
        self,
        prompt_name: str,
        user_input: dict,
        user: User,
        find_and_replace: dict = {},
    ) -> Response:

        # Identify the prompt
        prompt = self.get_prompt(prompt_name)

        # Replace the placeholders
        if find_and_replace:
            prompt.prompt = prompt.prompt.replace(**find_and_replace)  # type: ignore

        # If structured, add the schema
        if prompt.structure:
            prompt.prompt = prompt.prompt.replace(  # type: ignore
                "{structure}",
                json.dumps(prompt.structure, indent=4, ensure_ascii=False),
            )

        # Create the response
        return self.ai_client.responses.create(
            model=prompt.model or "gpt-4.1-nano",
            input=[
                {
                    "role": "developer",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt.prompt,
                        }
                    ],
                },
                user_input,  # type: ignore
            ],
            text={"format": {"type": "text"}},
            reasoning={},
            tools=[],
            temperature=0,
            max_output_tokens=2048,
            top_p=0,
            store=True,
            metadata={
                "service": prompt.service or "unknown",
                "query": prompt.query or "unknown",
                "version": str(prompt.version),
                "user_id": str(user.id),
                "user_email": user.email,
            },
        )
