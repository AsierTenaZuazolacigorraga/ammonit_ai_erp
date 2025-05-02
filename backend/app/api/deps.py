from collections.abc import Generator
from typing import Annotated

import jwt
from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User
from app.services.clients import ClientService
from app.services.orders import OrderService
from app.services.users import UserService
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from groq import Groq
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
# Users
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


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUserDep) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="El usuario no tiene suficientes privilegios"
        )
    return current_user


CurrentActiveSuperUserDep = Annotated[User, Depends(get_current_active_superuser)]


def user_service(session: SessionDep) -> UserService:
    return UserService(session=session)


UserServiceDep = Annotated[UserService, Depends(user_service)]


##########################################################################################
# Clients
##########################################################################################


def client_service(session: SessionDep) -> ClientService:
    return ClientService(session=session)


ClientServiceDep = Annotated[ClientService, Depends(client_service)]

##########################################################################################
# Orders
##########################################################################################


def order_service(
    session: SessionDep,
) -> OrderService:
    return OrderService(session=session)


OrderServiceDep = Annotated[OrderService, Depends(order_service)]
