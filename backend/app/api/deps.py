from collections.abc import Generator
from typing import Annotated

import jwt
from app.clients import OutlookClient
from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User
from app.repositories.orders import OrderRepository
from app.repositories.users import UserRepository
from app.services.orders import OrderService
from app.services.users import UserService
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from openai import OpenAI
from pydantic import ValidationError
from sqlmodel import Session

##########################################################################################
# Token
##########################################################################################

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]


##########################################################################################
# Session
##########################################################################################


def get_session(request: Request) -> Generator[Session, None, None]:
    """reuses the session if it already exists in the request/response cycle"""
    request_db_session = getattr(request.state, "db_session", None)
    if request_db_session and isinstance(request_db_session, Session):
        yield request_db_session
    else:
        with Session(engine) as session:
            yield session


SessionDep = Annotated[Session, Depends(get_session)]

##########################################################################################
# User
##########################################################################################


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se pudo validar las credenciales",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="El usuario no tiene suficientes privilegios"
        )
    return current_user


##########################################################################################
# AI
##########################################################################################


def get_ai_client(session: SessionDep, token: TokenDep) -> OpenAI:

    user = get_current_user(session, token)
    api_key = f"OPENAI_API_KEY_{user.full_name}"
    if hasattr(settings, api_key):
        return OpenAI(api_key=getattr(settings, api_key))
    else:
        raise HTTPException(
            status_code=403,
            detail="El usuario no se asocia a un cliente de inteligencia artificial",
        )


AIClientDep = Annotated[OpenAI, Depends(get_ai_client)]

##########################################################################################
# Email
##########################################################################################


def get_email_client(session: SessionDep, token: TokenDep) -> OutlookClient:

    user = get_current_user(session, token)
    return OutlookClient(
        settings.OUTLOOK_ID,
        settings.OUTLOOK_SECRET,
        user.email,
        settings.OUTLOOK_SCOPES,
    )


EmailClientDep = Annotated[OutlookClient, Depends(get_email_client)]

##########################################################################################
# Users
##########################################################################################


def user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(user_repository)]


def user_service(user_repository: UserRepositoryDep) -> UserService:
    return UserService(user_repository)


UserServiceDep = Annotated[UserService, Depends(user_service)]


##########################################################################################
# Orders
##########################################################################################


def order_repository(session: SessionDep) -> OrderRepository:
    return OrderRepository(session)


OrderRepositoryDep = Annotated[OrderRepository, Depends(order_repository)]


def order_service(
    order_repository: OrderRepositoryDep, ai_client: AIClientDep
) -> OrderService:
    return OrderService(order_repository, ai_client)


OrderServiceDep = Annotated[OrderService, Depends(order_service)]
