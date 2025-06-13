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
from app.easy.easy_params import *
from app.logger import get_logger
from app.models import OrderCreate
from app.services.clients import ClientService
from app.services.orders import OrderService
from app.services.users import UserService
from groq import Groq
from openai import OpenAI
from sqlmodel import Session

logger = get_logger(__name__)


async def main():

    if IS_LOCAL:

        logger.info("Running locally")
        with Session(engine) as session:
            user_service = UserService(session=session)
            for user in user_service.repository.get_all():

                # Only process desired user
                if user.email == EMAIL:

                    # Define orders service
                    order_service = OrderService(
                        session=session,
                    )
                    for order in ORDERS:
                        with open(order, "rb") as f:
                            base_document = f.read()
                        base_document_name = os.path.basename(order)

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
