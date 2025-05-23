import ast
import json
import uuid
from datetime import datetime

from app.core.config import settings
from app.models import Client, ClientCreate, ClientUpdate, OrderCreate
from app.repositories.base import CRUDRepository
from app.services.users import UserService
from openai import OpenAI
from pydantic import BaseModel
from sqlmodel import Session

ClientExample = Client(
    name="ClientExample",
    clasifier="""
El pedido muestra el nombre de cliente NearBy Electronics, y normalmente tiene las columnas de "ITEM", "QTY", "RATE", "AMOUNT".
""",
    base_document=b"",
    base_document_name="",
    base_document_markdown="""
*NearBy Electronics**  
3741 Glory Road, Jamestown,  
Tennessee, USA  
38556  

**Invoice# NL57EPAS7793742478**  
**Issue date**  
12-05-2023  

---

# NearBy Electronics  
We are here to serve you better. Reach out to us in case of any concern or feedbacks.

---

**BILL TO**  
Willis Koelpin  
Willis_Koelpin4@yahoo.com  
783-402-5895  
353 Cara Shoals  
Suchitlán  

**DETAILS**  
minim velit velit fugiat culpa  
deserunt ex aliquip cillum est  
aliqua ex amet amet  

**PAYMENT**  
Due date: 08-07-2023  

**$22337.7**  

---

| **ITEM**                  | **QTY** | **RATE** | **AMOUNT** |
|---------------------------|---------|----------|------------|
| Rustic Rubber Gloves       | 102     | 29       | $2958      |
| Fantastic Granite Salad    | 39      | 27       | $1053      |
| Small Fresh Salad          | 95      | 69       | $6555      |
| Fantastic Metal Chips      | 67      | 49       | $3283      |
| Refined Cotton Pants       | 79      | 72       | $5688      |
| Ergonomic Concrete Towels  | 35      | 22       | $770       |

---

**Subtotal**  
$20307  

**Tax %** 
""",
    content_processed="""
Código Pedido;Código Item Propio;Código Item Cliente;Descripción;Cantidad;Precio Unitario;Fecha de entrega
NL57EPAS7793742478;;Rustic Rubber Gloves;Rustic Rubber Gloves;102;29;2023-07-08
NL57EPAS7793742478;;Fantastic Granite Salad;Fantastic Granite Salad;39;27;2023-07-08
NL57EPAS7793742478;;Small Fresh Salad;Small Fresh Salad;95;69;2023-07-08
NL57EPAS7793742478;;Fantastic Metal Chips;Fantastic Metal Chips;67;49;2023-07-08
NL57EPAS7793742478;;Refined Cotton Pants;Refined Cotton Pants;79;72;2023-07-08
NL57EPAS7793742478;;Ergonomic Concrete Towels;Ergonomic Concrete Towels;35;22;2023-07-08
""",
    structure={
        "name": "order",
        "schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "description": "Los item en el pedido",
                    "items": {"$ref": "#/$defs/item"},
                },
            },
            "required": ["items"],
            "additionalProperties": False,
            "$defs": {
                "item": {
                    "type": "object",
                    "properties": {
                        "Código Pedido": {
                            "type": "string",
                            "description": "El código/número genérico del pedido. Repítelo para cada item.",
                        },
                        "Código Item Cliente": {
                            "type": "string",
                            "description": "El código del item",
                        },
                        "Descripción": {
                            "type": "string",
                            "description": "La descripción del item",
                        },
                        "Cantidad": {
                            "type": "integer",
                            "description": "La cantidad de items a pedir",
                        },
                        "Precio Unitario": {
                            "type": "number",
                            "description": "El precio unitario del item",
                        },
                        "Fecha de entrega": {
                            "type": "string",
                            "description": "La fecha de entrega del item (proporciona la fecha en el formato 'DD-MM-YYYY HH:MM:SS')",
                        },
                    },
                    "required": [
                        "Código Pedido",
                        "Código Item Cliente",
                        "Descripción",
                        "Cantidad",
                        "Precio Unitario",
                        "Fecha de entrega",
                    ],
                    "additionalProperties": False,
                }
            },
        },
        "strict": True,
    },
    additional_info="",
    owner_id=uuid.uuid4(),
)


class ClientService:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.repository = CRUDRepository[Client](Client, session)
        self.user_service = UserService(session)

        # Initialize clients
        self.ai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def create(self, client_create: ClientCreate, owner_id: uuid.UUID) -> Client:

        class ClientProposalStructure(BaseModel):
            codigo_pedido: str
            codigo_item_cliente: str
            descripcion: str
            cantidad: str
            precio_unitario: str
            fecha_entrega: str

        client_proposal = ClientExample.model_copy()

        response = self.ai_client.responses.parse(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"""
El usuario te proporcionará:
- Un texto en formato markdown que representa un pedido de cliente
- Una tabla en formato csv que representa la extracción de datos desde ese pedido

Tu tarea, es proporcionar para cada columna de la tabla csv, unas indicaciones de como extraer los
datos desde el documento markdown. Las indicaciones han de ser genéricas, y no específicas del pedido
actual. Es decir, no incluyas los datos de las celdas de la tabla csv, sino que
indica en que parte del documento (que columna, al lado de que texto) se encuentran los datos.

Por ejemplo, imaginémonos que el pedido tiene este contenido:

```
{client_proposal.base_document_markdown}
```

Y la tabla csv extraída del pedido es esta:

```
{client_proposal.content_processed}
```

Entonces, lo que deberías responder es:
```
"Código Pedido": "Aparece después del texto 'Invoice#' en la primera página.",
"Código Item Cliente": "En la columna 'ITEM'.",
"Descripción": "Utiliza el mismo valor que la columna 'ITEM'.",
"Cantidad": "En la columna 'QTY'.",
"Precio Unitario": "En la columna 'RATE'.",
"Fecha de entrega": "Proporciona la fecha en el formato 'DD-MM-YYYY HH:MM:SS'.",
```
   """,
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": client_create.content_processed or "",
                        }
                    ],
                },
            ],
            text_format=ClientProposalStructure,
            reasoning={},
            tools=[],
            temperature=0,
            max_output_tokens=2048,
            top_p=0,
            store=True,
        )
        if response.output_parsed is None:
            raise ValueError("Failed to parse the client proposal structure")

        client_proposal.structure["schema"]["$defs"]["item"]["properties"][
            "Código Pedido"
        ]["description"] += response.output_parsed.codigo_pedido
        client_proposal.structure["schema"]["$defs"]["item"]["properties"][
            "Código Item Cliente"
        ]["description"] += response.output_parsed.codigo_item_cliente
        client_proposal.structure["schema"]["$defs"]["item"]["properties"][
            "Descripción"
        ]["description"] += response.output_parsed.descripcion
        client_proposal.structure["schema"]["$defs"]["item"]["properties"]["Cantidad"][
            "description"
        ] += response.output_parsed.cantidad
        client_proposal.structure["schema"]["$defs"]["item"]["properties"][
            "Precio Unitario"
        ]["description"] += response.output_parsed.precio_unitario
        client_proposal.structure["schema"]["$defs"]["item"]["properties"][
            "Fecha de entrega"
        ]["description"] += response.output_parsed.fecha_entrega

        client_create.structure = client_proposal.structure
        return self.repository.create(
            Client.model_validate(client_create, update={"owner_id": owner_id})
        )

    def get_all(self, skip: int, limit: int, owner_id: uuid.UUID) -> list[Client]:
        return self.repository.get_all_by_kwargs(
            skip=skip,
            limit=limit,
            **{"owner_id": owner_id},
        )

    def get_by_id(self, id: uuid.UUID) -> Client:
        client = self.repository.get_by_id(id)
        if not client:
            raise ValueError("Client not found")
        return client

    def get_count(self, owner_id: uuid.UUID) -> int:
        return self.repository.count_by_kwargs(**{"owner_id": owner_id})

    def delete(self, id: uuid.UUID) -> None:
        self.repository.delete(id)

    def update(self, client_update: ClientUpdate, id: uuid.UUID) -> Client:
        client = self.get_by_id(id)
        if not client:
            raise ValueError("Client not found")
        return self.repository.update(
            client, update=client_update.model_dump(exclude_unset=True)
        )

    async def get_proposal(
        self, base_document: bytes, base_document_name: str, id: uuid.UUID
    ) -> Client:

        from app.services.orders import process

        client_proposal = ClientExample.model_copy(
            update={
                "owner_id": id,
                "base_document": base_document,
                "base_document_name": base_document_name,
            }
        )

        user, client, order = await process(
            order_create=OrderCreate(
                base_document=base_document,
                base_document_name=base_document_name,
            ),
            ai_client=self.ai_client,
            clients=[client_proposal],
            user=self.user_service.get_by_id(id),
        )
        response = self.ai_client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"""
El usuario te proporcionará un texto markdown, que corresponde a un pedido de cliente.
Tu tarea, es responder al usuario con una frase que:
- Unequívocamente, pueda utilizarse para clasificar el pedido al cliente pertinente,
  habilitando al que lo lea de relacionar el pedido actual al cliente correcto
- Se centre en patrones genéricos que puedan utilizarse para esa clasificación
  (palabras genéricas clave, cabeceras, formato...)
- No se centre en detalles particulares del actual pedido (número de pedido.. etc,
  ya que eso cambiará de pedido en pedido)

Responde con una frase de no más de 50 palabras, y en español.
En la respuesta, menciona siempre el nombre del cliente.

Por ejemplo, imaginémonos que el pedido tiene este contenido:

```
{client_proposal.base_document_markdown}
```

Entonces, la frase que deberías responder es:

```
{client_proposal.clasifier}
```
    """,
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": order.base_document_markdown or "",
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

        client.base_document_markdown = order.base_document_markdown
        client.content_processed = order.content_processed
        client.clasifier = response.output_text
        return client
