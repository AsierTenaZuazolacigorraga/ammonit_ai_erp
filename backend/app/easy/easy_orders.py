import asyncio
import base64
import datetime
import os
import pprint
import tempfile
from datetime import datetime, timezone

import pandas as pd
from app.core.config import settings
from app.core.db import engine
from app.logger import get_logger
from app.models import OrderCreate
from app.services.clients import ClientService
from app.services.orders import OrderService
from app.services.users import UserService
from groq import Groq
from openai import OpenAI
from sqlmodel import Session

logger = get_logger(__name__)

ORDER_1 = r"/home/atena/my_projects/iot_bind/.gitignores/Invoice 1/output1.pdf"
ORDER_danobat = (
    r"/home/atena/my_projects/iot_bind/.gitignores/Eskariak/DANOBAT/100083396.pdf"
)
ORDER_fagor = (
    r"/home/atena/my_projects/iot_bind/.gitignores/Eskariak/FAGOR/5B-20575.pdf"
)
ORDER_inola = r"/home/atena/my_projects/iot_bind/.gitignores/Eskariak/INOLA/87-25.pdf"
ORDER_matisa = (
    r"/home/atena/my_projects/iot_bind/.gitignores/Eskariak/MATISA/CF2503-87388.pdf"
)
ORDER_ulma1 = r"/home/atena/my_projects/iot_bind/.gitignores/Eskariak/ULMA/598153.pdf"
ORDER_ulma2 = r"/home/atena/my_projects/iot_bind/.gitignores/Eskariak/ULMA/4595390.pdf"
ORDER = ORDER_ulma2


async def main():
    with Session(engine) as session:
        user_service = UserService(session=session)
        for user in user_service.repository.get_all():

            # Only process desired user
            if user.full_name == "Asier":

                # Define orders service
                order_service = OrderService(
                    session=session,
                    ai_client=OpenAI(api_key=settings.OPENAI_API_KEY),
                    groq_client=Groq(api_key=settings.GROQ_API_KEY),
                )
                with open(ORDER, "rb") as f:
                    base_document = f.read()
                base_document_name = os.path.basename(ORDER)

                order = await order_service.create(
                    order_create=OrderCreate(
                        base_document=base_document or None,
                        base_document_name=base_document_name or None,
                    ),
                    owner_id=user.id,
                )
                logger.info(order.content_processed)

                # Check if out_document is None
                if order.content_processed is None:
                    raise ValueError("The order output document is None.")


if __name__ == "__main__":
    asyncio.run(main())
