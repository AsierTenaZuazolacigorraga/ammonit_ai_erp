import os
import uuid

from app.core.config import settings
from app.core.db import engine
from app.logger import get_logger
from app.services.emails import EmailService
from app.services.orders import OrderService
from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI
from sqlmodel import Session

logger = get_logger(__name__)

################################################################

load_dotenv()

OUTLOOK_ID = os.getenv("OUTLOOK_ID")
OUTLOOK_SECRET = os.getenv("OUTLOOK_SECRET")
# OUTLOOK_EMAIL = "asier.tena.zu@outlook.com"
OUTLOOK_EMAIL = "alberdi.autom@outlook.com"
# OUTLOOK_EMAIL = "asier.tena.zu@ammonitammonit.onmicrosoft.com"

################################################################


def main():

    # Create a database session
    with Session(engine) as session:

        # Initialize required services
        order_service = OrderService(
            session=session,
            ai_client=OpenAI(api_key=settings.OPENAI_API_KEY),
            groq_client=Groq(api_key=settings.GROQ_API_KEY),
        )

        # Create email service instance
        email_service = EmailService(
            session=session,
            order_service=order_service,
            id=OUTLOOK_ID,
            secret=OUTLOOK_SECRET,
            email=OUTLOOK_EMAIL,
        )

        messages = list(
            email_service.account.mailbox()
            .inbox_folder()
            .get_messages(limit=50, order_by="receivedDateTime desc")
        )

        if messages:
            for message in messages[:5]:  # Limit to the first 5 messages
                print(f"Email read:\n\n")
                print(f"Subject: {message.subject}")
                print(f"Sender: {message.sender}")
                print(f"Date: {message.created}")
                print(f"Content: {message.body}")
        else:
            print("No messages found.")


if __name__ == "__main__":
    main()
