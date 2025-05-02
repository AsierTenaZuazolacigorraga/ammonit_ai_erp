import asyncio
import threading
import time
import traceback

from app.core.config import settings
from app.core.db import engine
from app.logger import get_logger
from app.services.clients import ClientService
from app.services.emails import EmailService
from app.services.orders import OrderService
from app.services.users import UserService
from groq import Groq
from openai import OpenAI
from sqlmodel import Session

logger = get_logger(__name__)


class Scheduler:
    def __init__(self):
        self.tasks = []
        self.lock = threading.Lock()

    def add_task(self, func, period):
        """Adds a new task that will run every 'period' seconds. The task should accept a session parameter."""
        thread = threading.Thread(target=self._run_task, args=(func, period))
        thread.daemon = True
        with self.lock:
            self.tasks.append(thread)
        thread.start()
        logger.info("Task %s added with period %s sec.", func.__name__, period)

    def _run_task(self, func, period):
        """Runs the given task in an infinite loop with a database session, handling exceptions."""
        while True:
            with Session(engine) as session:
                try:
                    # Call the function, potentially capturing a coroutine
                    result = func(session)
                    # Check if the result is awaitable (a coroutine)
                    if asyncio.iscoroutine(result):
                        # If it is, run it using asyncio.run
                        asyncio.run(result)
                    # Otherwise, assume the function was synchronous and already executed.
                except Exception as e:
                    logger.error("Error in task %s: %s", func.__name__, e)
                    logger.debug("Traceback: %s", traceback.format_exc())
            time.sleep(period)


def task_health_check(session):
    logger.info("task_health_check: Running")


async def task_for_each_user_email_service_fetch(session, user):

    logger.info(
        f"task_email_service_fetch: {user.full_name} | email: {user.email} | id: {user.id}"
    )

    # Define orders service
    order_service = OrderService(
        session,
    )

    # Define emails service
    email_service = EmailService(
        session,
        order_service,
        settings.OUTLOOK_ID,
        settings.OUTLOOK_SECRET,
        user.email,
    )

    # Fetch emails
    await email_service.fetch(owner_id=user.id)


def main():
    sched = Scheduler()

    # Add tasks
    sched.add_task(task_health_check, 15)

    # Add tasks for each user
    with Session(engine) as session:
        user_service = UserService(session)
        for user in [
            user for user in user_service.get_all(skip=0, limit=100) if user.is_active
        ]:
            sched.add_task(
                lambda s, u=user: task_for_each_user_email_service_fetch(s, u), 10
            )

    # Keep the main thread running for further task additions or a graceful exit.
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped.")


if __name__ == "__main__":
    main()
