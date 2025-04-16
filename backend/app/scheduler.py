import threading
import time
import traceback

from app.core.config import settings
from app.core.db import engine
from app.logger import get_logger
from app.repositories.clients import ClientRepository
from app.repositories.emails import EmailRepository
from app.repositories.orders import OrderRepository
from app.repositories.users import UserRepository
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
                    func(session)
                except Exception as e:
                    logger.error("Error in task %s: %s", func.__name__, e)
                    logger.debug("Traceback: %s", traceback.format_exc())
            time.sleep(period)


def task_health_check(session):
    logger.info("task_health_check: Running")


def task_for_each_user_email_service_fetch(session, user):

    logger.info(
        f"task_email_service_fetch: {user.full_name} | email: {user.email} | id: {user.id}"
    )

    # Define orders service
    order_service = OrderService(
        OrderRepository(session),
        ClientService(ClientRepository(session)),
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

    # Fetch emails
    email_service.fetch(owner_id=user.id)


def main():
    sched = Scheduler()

    # Add tasks
    sched.add_task(task_health_check, 15)

    # Add tasks for each user
    with Session(engine) as session:
        user_service = UserService(UserRepository(session))
        for user in [
            user for user in user_service.repository.get_all() if user.is_active
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
