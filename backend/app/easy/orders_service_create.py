# app/scheduler_main.py
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
from app.repositories.emails import EmailRepository
from app.repositories.orders import OrderRepository
from app.repositories.users import UserRepository
from app.services.emails import EmailService
from app.services.orders import (
    OrderDanobat,
    OrderFagor,
    OrderInola,
    OrderMatisa,
    OrderService,
    OrderUlma,
)
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


def main():
    with Session(engine) as session:
        user_service = UserService(UserRepository(session))
        for user in user_service.repository.get_all():

            # Only process desired user
            if user.full_name == "Asier":

                # Define orders service
                order_service = OrderService(
                    OrderRepository(session),
                    OpenAI(api_key=getattr(settings, "OPENAI_API_KEY")),
                    Groq(api_key=getattr(settings, "GROQ_API_KEY")),
                )
                with open(ORDER, "rb") as f:
                    in_document = f.read()
                in_document_name = os.path.basename(ORDER)

                order = order_service.process(
                    order_create=OrderCreate(
                        date_local=datetime.now(),
                        date_utc=datetime.now(timezone.utc),
                        in_document=in_document or None,
                        in_document_name=in_document_name or None,
                    ),
                    owner_id=user.id,
                )
                logger.info(order.out_document)

                # Check if out_document is None
                if order.out_document is None:
                    raise ValueError("The order output document is None.")

                with tempfile.NamedTemporaryFile(suffix=".csv", delete=True) as f:
                    f.write(order.out_document)
                    f.flush()
                    df = pd.read_csv(f.name, sep=";")
                    print(df)
                    pretty_df = pprint.pformat(
                        df.to_dict(orient="records")
                    )  # Convert DataFrame to a list of dictionaries
                    print(pretty_df)
            else:
                logger.warning(
                    "El usuario no se asocia a un cliente de inteligencia artificial"



if __name__ == "__main__":
    main()

