# app/scheduler_main.py
import asyncio
import logging

from app.core.config import settings
from app.core.db import engine
from app.logger import get_logger
from app.repositories.emails import EmailRepository
from app.repositories.orders import OrderRepository
from app.repositories.users import UserRepository
from app.services.emails import EmailService
from app.services.orders import OrderService
from app.services.users import UserService
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from openai import OpenAI
from sqlmodel import Session

logger = get_logger(__name__)
scheduler = AsyncIOScheduler()


def schedules_start(scheduler: AsyncIOScheduler) -> None:
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    scheduler.start()

    # Get all users
    with Session(engine) as session:
        user_service = UserService(UserRepository(session))
        for user in user_service.repository.get_all():

            # Define the services
            api_key = f"OPENAI_API_KEY_{user.full_name}"
            if hasattr(settings, api_key):

                # Define orders service
                ai_client = OpenAI(api_key=getattr(settings, api_key))
                order_service = OrderService(OrderRepository(session), ai_client)

                # Define emails service
                email_service = EmailService(
                    EmailRepository(session),
                    order_service,
                    settings.OUTLOOK_ID,
                    settings.OUTLOOK_SECRET,
                    user.email,
                    settings.OUTLOOK_SCOPES,
                )

                email_service.fetch(owner_id=user.id)

                # Add jobs
                scheduler.add_job(
                    email_service.fetch,
                    "interval",
                    seconds=10,
                    kwargs={"owner_id": user.id},
                    max_instances=1,
                )
            else:
                logger.warning(
                    "El usuario no se asocia a un cliente de inteligencia artificial"
                )


def schedules_finish(scheduler: AsyncIOScheduler) -> None:
    pass


def main():
    logger.info("Starting scheduler process.")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Schedule starting the scheduler after the loop starts running.
    loop.call_soon(lambda: schedules_start(scheduler))

    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        schedules_finish(scheduler)


if __name__ == "__main__":
    main()
