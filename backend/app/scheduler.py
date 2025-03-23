import asyncio
import logging

import nest_asyncio
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
from groq import Groq
from openai import OpenAI
from sqlmodel import Session

logger = get_logger(__name__)
scheduler = AsyncIOScheduler()

# Store active job IDs by user ID to avoid duplicates
user_jobs = {}


def check_for_new_users():
    """Check for new users and set up email fetch jobs for them."""
    logger.info("Checking for new users...")
    with Session(engine) as session:
        user_service = UserService(UserRepository(session))
        all_active_users = [
            user.id for user in user_service.repository.get_all() if user.is_active
        ]

        # Find users that don't have jobs yet
        new_users = [
            user_id for user_id in all_active_users if user_id not in user_jobs
        ]

        # Set up jobs for new users
        if new_users:
            for user_id in new_users:
                setup_user_job(session, user_id)

        # Clean up jobs for deactivated users
        users_to_remove = [
            user_id for user_id in user_jobs if user_id not in all_active_users
        ]
        for user_id in users_to_remove:
            job_id = user_jobs[user_id]
            scheduler.remove_job(job_id)
            del user_jobs[user_id]
            logger.info(f"Removed job for deactivated user ID: {user_id}")


def setup_user_job(session, user_id):
    """Set up an email fetch job for a specific user."""
    try:
        user_repository = UserRepository(session)
        user = user_repository.get_by_id(user_id)

        if user and user.is_active:
            logger.info(f"Setting up job for user: {user.full_name}")
            logger.info(f"Setting up job for user email: {user.email}")
            logger.info(f"Setting up job for user id: {user.id}")

            # Define orders service
            order_service = OrderService(
                OrderRepository(session),
                OpenAI(api_key=settings.OPENAI_API_KEY),
                Groq(api_key=settings.GROQ_API_KEY),
            )

            # Define emails service
            email_service = EmailService(
                EmailRepository(session),
                order_service,
                settings.OUTLOOK_ID,
                settings.OUTLOOK_SECRET,
                user.email,
                settings.OUTLOOK_SCOPES,
            )

            # Initial fetch
            email_service.fetch(owner_id=user.id)

            # Add scheduled job
            job = scheduler.add_job(
                email_service.fetch,
                "interval",
                seconds=10,
                kwargs={"owner_id": user.id},
                max_instances=1,
                id=f"email_fetch_{user.id}",  # Use a predictable ID for the job
            )

            # Store the job ID for future reference
            user_jobs[user.id] = job.id
            logger.info(f"Added job for user ID: {user.id}")
    except Exception as e:
        logger.error(f"Error setting up job for user ID {user_id}: {e}")


def schedules_start(scheduler: AsyncIOScheduler) -> None:
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    scheduler.start()

    # Add job to check for new users every minute
    scheduler.add_job(
        check_for_new_users,
        "interval",
        minutes=1,
        id="check_new_users",
        max_instances=1,
    )

    # Initial check for users
    check_for_new_users()


def schedules_finish(scheduler: AsyncIOScheduler) -> None:
    scheduler.shutdown()


def main():
    logger.info("Starting scheduler process.")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Apply nest_asyncio to allow nested event loops
    nest_asyncio.apply(loop)

    # Schedule starting the scheduler after the loop starts running.
    loop.call_soon(lambda: schedules_start(scheduler))

    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        schedules_finish(scheduler)


if __name__ == "__main__":
    main()
