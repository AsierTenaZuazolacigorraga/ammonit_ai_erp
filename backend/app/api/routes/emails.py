from app.api.deps import CurrentUserDep, EmailServiceDep
from app.services.emails import EmailService
from app.services.orders import OrderService
from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlmodel import Session

router = APIRouter(prefix="/emails", tags=["emails"])


@router.post("/outlook-token-step-1/", response_model=str)
def create_outlook_token_step_1(
    email_service: EmailServiceDep,
) -> str:
    """
    Create outlook token step 1.
    """
    url = email_service.create_outlook_token_step_1()
    return url


class OutlookTokenStep2(BaseModel):
    code: str


@router.post("/outlook-token-step-2/")
def create_outlook_token_step_2(
    data: OutlookTokenStep2,
    email_service: EmailServiceDep,
):
    """
    Create outlook token step 2.
    """
    success = email_service.create_outlook_token_step_2(data.code)
    if not success:
        raise HTTPException(status_code=400, detail="Authentication failed.")
    return {"detail": "Authentication successful."}
