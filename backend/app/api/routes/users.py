import uuid
from typing import Any

from app.api.deps import (
    CurrentUserDep,
    EmailServiceDep,
    UserServiceDep,
    get_current_active_superuser,
    get_current_user,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import (
    EmailCreate,
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUserDep) -> Any:
    """
    Get current user.
    """
    if current_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return current_user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, user_service: UserServiceDep, user_in: UserUpdateMe, current_user: CurrentUserDep
) -> Any:
    """
    Update own user.
    """
    if current_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if user_in.email:
        existing_user = user_service.get_by_email(email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="El usuario con este email ya existe"
            )
    user_service.update(user_update=user_in, id=current_user.id)
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, user_service: UserServiceDep, body: UpdatePassword, current_user: CurrentUserDep
) -> Any:
    """
    Update own password.
    """
    if current_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400,
            detail="La nueva contraseña no puede ser la misma que la actual",
        )
    user_service.update(
        user_update=UserUpdate(password=body.new_password), id=current_user.id
    )
    return Message(message="Contraseña actualizada correctamente")


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
def create_user(
    *, user_service: UserServiceDep, email_service: EmailServiceDep, user_in: UserCreate
) -> Any:
    """
    Create new user.
    """
    user = user_service.get_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="El usuario con este email ya existe en el sistema.",
        )
    user = user_service.create(user_create=user_in)
    email_service.email_create(
        email_create=EmailCreate(email=user_in.email), owner_id=user.id
    )

    return user


@router.get(
    "/",
    dependencies=[Depends(get_current_user)],
    response_model=UsersPublic,
)
def read_users(user_service: UserServiceDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """
    users = user_service.get_all(skip=skip, limit=limit)
    return UsersPublic(
        data=[UserPublic.model_validate(user) for user in users],
        count=user_service.get_count(),
    )


@router.get(
    "/{id}",
    response_model=UserPublic,
)
def read_user(
    id: uuid.UUID, user_service: UserServiceDep, current_user: CurrentUserDep
) -> Any:
    """
    Get a specific user by id.
    """
    user = user_service.get_by_id(id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="El usuario no tiene suficientes privilegios",
        )
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.patch(
    "/{id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    user_service: UserServiceDep,
    id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """

    user = user_service.get_by_id(id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="El usuario con este id no existe en el sistema",
        )
    if user_in.email:
        existing_user = user_service.get_by_email(email=user_in.email)
        if existing_user and existing_user.id != id:
            raise HTTPException(
                status_code=409, detail="El usuario con este email ya existe"
            )

    user = user_service.update(user_update=user_in, id=id)
    return user


@router.delete("/{id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    user_service: UserServiceDep, current_user: CurrentUserDep, id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    user = user_service.get_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Los superusuarios no pueden eliminarse a sí mismos"
        )
    user_service.delete(id)
    return Message(message="Usuario eliminado correctamente")
