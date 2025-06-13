import asyncio
import json
import os

import pandas as pd
from app.core.config import settings
from app.core.db import engine
from app.easy.easy_params import *
from app.logger import get_logger
from app.models import OrderCreate
from app.services.clients import ClientService
from app.services.orders import OrderService, parse_document_2_md, preprocess_document
from app.services.users import UserService
from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI
from sqlmodel import Session

logger = get_logger(__name__)


load_dotenv()

fields_description = """
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
"""
fields_format = """
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
"""
additional_rules = """
- La empresa para la que trabajas es Alberdi Mekanizatuak (C.I.F. B01896885). Bajo ningún concepto puedes identificar como cliente a Alberdi Mekanizatuak
"""
particular_rules = """
- Para pedidos del cliente Ulma Packaging:
  - En el documento, el número de pedido suele acompañarse de cierto texto dentro de paréntesis (). Has de ignorar ese texto en paréntesis y considerar soloamente el valor
    númerico para el campo order_number

- Para pedidos del cliente Fagor Arrasate S.COOP:
  - El número de pedido suele aparecer al lado de la palabra "Eskari"
"""

DEVELOPER_PROMPT = f"""
# Objetivo

Eres un asistente especializado en extraer información estructurada de pedidos en formato markdown. Tu tarea es, dada la transcripción en markdown de un documento de pedido
(que puede variar en formato, contenido,columnas, distribución o idioma), identificar y normalizar los siguientes datos:

{fields_description}

# Reglas de extracción y normalización

- Fechas:
  - Reconoce formatos comunes (dd/mm/yyyy, d/m/yy, yyyy-mm-dd, etc.) y normalizar a ISO 8601 (“YYYY-MM-DD”)
  - Si hay varias fechas generales (p.ej. “FECHA: 25/02/2025” y “Lugar de entrega” con fecha distinta), identifica la fecha que se refiere a la entrega global, y descarta otras posibles fechas como fecha de emisión
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
- Detecta etiquetas con tolerancia: p.ej. “Nº:”, “Número de pedido”, “Order No”, “Pedido”, u otras variaciones. Usa patrones y proximidad semántica
- Tablas markdown: manejar filas que continúan descripción en filas siguientes con celdas vacías en columnas clave. Concatenar texto de descripción con espacios o saltos según convenga
- Columnas variables: nombres de columna pueden variar (“Artículo”, “Código”, “Referencia”, “Descripción”, etc.). Usa cercanía semántica:
  - Si una columna parece contener un número largo alfanumérico, puede ser code;
  - Si es texto alfabético extenso, description;
  - Si contiene “€” o patrón de precio, price;
  - Si contiene fecha, delivery_date
- Si no encuentras un campo, establece valor null
- Ignora celdas vacías o de control interno irrelevantes
- Considera posibles idiomas (español, inglés, euskera u otro) en etiquetas de campo: por ejemplo “Entrega”, “Delivery”, “Entrega prevista”, “Entrega-Data” (euskera). Trata de inferir el concepto
{additional_rules}

# Reglas particulares
{particular_rules}

# Estructura

Responde solo con un JSON válido que siga esta estructura:

{fields_format}
"""

EVAL_PROMPT = f"""
La respuesta se considerará como "Fail":
1. Si la respuesta no se proporciona en el formato .json
2. Si el json proporcionado no incluye todos los siguientes campos
{fields_format}
Donde los campos significan:
{fields_description}
3. Si, después de que analices profundamente la pregunta y el contexto del usuario, entiendes que cualquiera de los campos de la respuesta:
- Está mal completado, o la información añadida en el campo está incompleta, por cualquier motivo
- Especial atención a los campos que tienen un valor null asociado. Asegúrate de que en el documento original, efectivamente no existe información
  sobre el campo en cuestión y por lo tanto es un null válido

De lo contrario, la respuesta se considerará como "Pass"

Notas:
- Se admite y se entiende que "null" y null son equivalentes
"""

EVAL_ID = 11


async def main():

    logger.info("Running locally")
    with Session(engine) as session:

        # Define user service
        user_service = UserService(session=session)
        user = user_service.get_by_email(EMAIL)

        # Define orders service
        order_service = OrderService(
            session=session,
        )

        # Create a list to store the data
        data = []

        for order in ORDERS:
            with open(order, "rb") as f:
                base_document = f.read()
            base_document_name = os.path.basename(order)

            # Preprocess document
            document = preprocess_document(base_document, base_document_name, user)

            # Parse document to md
            md = await parse_document_2_md(
                order_service.ai_client, document, base_document_name
            )

            response = order_service.ai_client.responses.create(
                model="gpt-4.1-nano",
                input=[
                    {"role": "developer", "content": DEVELOPER_PROMPT},
                    {"role": "user", "content": md},
                ],
                text={"format": {"type": "text"}},
                reasoning={},
                tools=[],
                temperature=0,
                max_output_tokens=2048,
                top_p=0,
                store=True,
                metadata={"eval_id": str(EVAL_ID)},
            )

            print("\n\n--------------------------------\n\n")
            print("\n\n--------------------------------\n\n")
            print(md)
            print("\n\n--------------------------------\n\n")
            print(response.output_text)

            # Add the markdown content to our data list
            data.append(
                {
                    "input_mine": md,
                    "ground_truth_mine": response.output_text,
                    "output_mine": "",
                }
            )

        # Create DataFrame and save to CSV
        df = pd.DataFrame(data)
        df.to_csv(".gitignores/eval_data.csv", index=False)
        logger.info("CSV file created successfully")

        print(DEVELOPER_PROMPT)
        print(EVAL_PROMPT)


if __name__ == "__main__":
    asyncio.run(main())
