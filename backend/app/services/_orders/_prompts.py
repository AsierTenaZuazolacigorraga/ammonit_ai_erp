##########################################################################################
# Document to MD
##########################################################################################

DOCUMENT_2_MD_PROMPT = """
1. Lee el documento que se te proporciona
2. Comprende la estructura del texto y la visualización de los diferentes contenidos
3. Convierte el documento a texto markdown, asegurándote de mantener la misma estructura y visualización del texto
4. Responde solo con el texto markdown, usando el mismo idioma que se usa en el documento

Notas:
- Si el documento contiene imágenes, transcríbelas e inclúyelas en el texto markdown
- Si las imágenes contienen texto, incluye el texto en el texto markdown
"""

##########################################################################################
# MD to Order
##########################################################################################

FIELDS_DESCRIPTION = """
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

FIELDS_FORMAT = """
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

MD_2_ORDER_PROMPT = f"""
# Objetivo

Eres un asistente especializado en extraer información estructurada de pedidos en formato markdown. Tu tarea es, dada la transcripción en markdown de un documento de pedido
(que puede variar en formato, contenido,columnas, distribución o idioma), identificar y normalizar los siguientes datos:

{FIELDS_DESCRIPTION}

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
{{ADDITIONAL_RULES}}

# Reglas particulares para algunos clientes
{{PARTICULAR_RULES}}

# Estructura

Responde solo con un JSON válido que siga esta estructura:

{FIELDS_FORMAT}
"""

EVAL_PROMPT = f"""
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
"""

##########################################################################################
# Schemas
##########################################################################################

ORDER_SCHEMA = {
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
}

ORDER_COLUMS_MAPPING = {
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
}
