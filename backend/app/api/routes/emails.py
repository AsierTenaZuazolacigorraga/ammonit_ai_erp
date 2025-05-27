import uuid

from app.api.deps import CurrentUserDep, EmailServiceDep
from app.models import EmailCreate, EmailPublic, EmailsPublic, EmailUpdate, Message
from app.services.emails import EmailService
from app.services.orders import OrderService
from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlmodel import Session

router = APIRouter(prefix="/emails", tags=["emails"])


@router.get("/", response_model=EmailsPublic)
def read_emails(
    email_service: EmailServiceDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 100,
) -> EmailsPublic:
    """
    Retrieve emails.
    """
    emails = email_service.get_all(skip=skip, limit=limit, owner_id=current_user.id)
    count = email_service.get_count(owner_id=current_user.id)
    email_service.load_all(owner_id=current_user.id)
    if email_service.accounts:
        emails_public = [
            EmailPublic.model_validate(
                email,
                update={
                    "is_connected": email_service.accounts[email.email][
                        "account"
                    ].is_authenticated
                },
            )
            for email in emails
        ]
    else:
        emails_public = [
            EmailPublic.model_validate(
                email,
                update={},
            )
            for email in emails
        ]
    return EmailsPublic(
        data=emails_public,
        count=count,
    )


@router.post("/", response_model=EmailPublic)
def create_email(
    email_service: EmailServiceDep,
    current_user: CurrentUserDep,
    email_in: EmailCreate,
) -> EmailPublic:
    """
    Create new email.
    """
    email = email_service.get_by_email(email=email_in.email)
    if email:
        raise HTTPException(
            status_code=400,
            detail="Este email ya existe en el sistema.",
        )

    email = email_service.email_create(email_create=email_in, owner_id=current_user.id)
    email_service.load_by_id(id=email.id)
    return EmailPublic.model_validate(
        email,
        update={
            "is_connected": email_service.accounts[email.email][
                "account"
            ].is_authenticated
        },
    )


@router.post("/outlook-token-step-1/", response_model=str)
def create_outlook_token_step_1(
    email_service: EmailServiceDep,
    email_in: EmailCreate,
) -> str:
    """
    Create outlook token step 1.
    """
    email = email_service.get_by_email(email=email_in.email)
    if not email:
        raise HTTPException(
            status_code=400,
            detail="Este email no existe en el sistema.",
        )
    email_service.load_by_id(id=email.id)
    url = email_service.create_outlook_token_step_1(email=email_in.email)
    return url


class OutlookTokenStep2(BaseModel):
    code: str


@router.post("/outlook-token-step-2/")
def create_outlook_token_step_2(
    data: OutlookTokenStep2,
    email_service: EmailServiceDep,
    email_in: EmailCreate,
) -> dict[str, str]:
    """
    Create outlook token step 2.
    """
    email = email_service.get_by_email(email=email_in.email)
    if not email:
        raise HTTPException(
            status_code=400,
            detail="Este email no existe en el sistema.",
        )
    email_service.load_by_id(id=email.id)
    success = email_service.create_outlook_token_step_2(
        email=email_in.email, code=data.code
    )
    if not success:
        raise HTTPException(status_code=400, detail="Authentication failed.")
    return {"detail": "Authentication successful."}


@router.delete("/{id}/")
def delete_email(
    email_service: EmailServiceDep,
    current_user: CurrentUserDep,
    id: uuid.UUID,
) -> Message:
    """
    Delete an email.
    """
    email = email_service.get_by_id(id)
    if not email:
        raise HTTPException(status_code=404, detail="Email no encontrado")
    if not current_user.is_superuser and (email.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Permisos insuficientes")
    email_service.delete(id=id)
    return Message(message="Email eliminado correctamente")


@router.patch(
    "/{id}/",
    response_model=EmailPublic,
)
def update_email(
    *,
    email_service: EmailServiceDep,
    current_user: CurrentUserDep,
    id: uuid.UUID,
    email_in: EmailUpdate,
) -> EmailPublic:
    """
    Update a email.
    """

    email = email_service.get_by_id(id)
    if not email:
        raise HTTPException(status_code=404, detail="Email no encontrado")
    if not current_user.is_superuser and (email.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Permisos insuficientes")
    email = email_service.update(email_update=email_in, id=id)
    return EmailPublic.model_validate(email)
