import os
import uuid

from app.core.config import settings
from app.core.db import engine
from app.easy.easy_params import *
from app.logger import get_logger
from app.services.emails import EmailService
from app.services.orders import OrderService
from app.services.users import UserService
from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI
from sqlmodel import Session

logger = get_logger(__name__)


def main():

    # Create source and destination paths
    source_path = os.path.join(os.getcwd(), "backend", ".gitignores", "azure_tokens")
    dest_path = os.path.join(os.getcwd(), ".gitignores", "azure_tokens")

    # Copy all files from source to destination
    for filename in os.listdir(source_path):
        source_file = os.path.join(source_path, filename)
        dest_file = os.path.join(dest_path, filename)

        # Copy file
        with open(source_file, "rb") as src, open(dest_file, "wb") as dst:
            dst.write(src.read())

    # Create a database session
    with Session(engine) as session:
        user_service = UserService(session=session)
        for user in user_service.repository.get_all():

            # Only process desired user
            if user.email == EMAIL:

                # Create email service instance
                email_service = EmailService(
                    session,
                )
                email_service.load_all(owner_id=user.id)

                for k, v in email_service.accounts.items():
                    print(f"Email: {k}")
                    account = v["account"]
                    messages = list(
                        account.mailbox()
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
