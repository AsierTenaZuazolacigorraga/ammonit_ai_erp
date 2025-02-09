import logging
from contextlib import asynccontextmanager

import sentry_sdk
from app.api.main import api_router
from app.core.config import settings
from app.core.exceptions import exception_handler
from app.middleware import DBSessionMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from starlette_context.middleware import RawContextMiddleware


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)


def print_a():
    print("a")


# Add lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):

    # Do something when api goes up
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    scheduler.start()
    scheduler.add_job(print_a, "interval", seconds=2)

    yield

    # Do something when api goes down


scheduler = AsyncIOScheduler()
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    DBSessionMiddleware,
    excluded_paths=["/api/v1/utils/"],
)
app.add_middleware(
    RawContextMiddleware,
    plugins=[
        # RequestIdPlugin(),
        # CorrelationIdPlugin(),
    ],
)

# Execption
app.add_exception_handler(Exception, exception_handler)

# Router
app.include_router(api_router, prefix=settings.API_V1_STR)
