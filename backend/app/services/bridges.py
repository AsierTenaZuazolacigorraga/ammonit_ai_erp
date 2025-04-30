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
from time import sleep
from typing import List, Union
from uuid import UUID

import pandas as pd
import PyPDF2
from app.logger import get_logger
from app.models import Client, Order, OrderCreate, OrderState, OrderUpdate
from app.repositories.base import CRUDRepository
from app.services.clients import ClientService
from app.services.users import UserService
from dotenv import load_dotenv
from fastapi import HTTPException
from groq import Groq
from llama_parse import LlamaParse, ResultType
from openai import OpenAI
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlmodel import Session

load_dotenv()

logger = get_logger(__name__)


class BridgeService:
    def __init__(
        self,
        session: Session,
    ) -> None:
        # self.repository = CRUDRepository[Bridge](Bridge, session)
        self.session = session

    def execute(self, *, order_update: OrderUpdate) -> OrderUpdate:

        try:
            sleep(10)
            raise NotImplementedError("ERP integration not implemented yet")
            order_update.state = OrderState.INTEGRATED
        except Exception as e:
            logger.error(f"Error integrating in ERP order: {e}")
            order_update.state = OrderState.ERROR
        order_update.erp_interaction_at = datetime.now(timezone.utc)

        return order_update
