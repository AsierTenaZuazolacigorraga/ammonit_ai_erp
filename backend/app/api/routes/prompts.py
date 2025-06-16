import uuid
from datetime import datetime, timezone
from typing import Any

from app.api.deps import CurrentUserDep, PromptServiceDep
from app.models import Message, PromptCreate, PromptPublic, PromptsPublic, PromptUpdate
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.get("/", response_model=PromptsPublic)
def read_prompts(
    prompt_service: PromptServiceDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 100,
) -> PromptsPublic:
    """
    Retrieve prompts.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Permisos insuficientes")
    prompts = prompt_service.get_all(skip=skip, limit=limit, owner_id=current_user.id)
    count = prompt_service.get_count(owner_id=current_user.id)
    return PromptsPublic(
        data=[PromptPublic.model_validate(prompt) for prompt in prompts],
        count=count,
    )


@router.get("/{id}/", response_model=PromptPublic)
def read_prompt(
    prompt_service: PromptServiceDep,
    current_user: CurrentUserDep,
    id: uuid.UUID,
) -> PromptPublic:
    """
    Get prompt by id.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Permisos insuficientes")
    prompt = prompt_service.get_by_id(id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    return PromptPublic.model_validate(prompt)


@router.post("/", response_model=PromptPublic)
async def create_prompt(
    prompt_service: PromptServiceDep,
    current_user: CurrentUserDep,
    prompt_create: PromptCreate,
) -> PromptPublic:
    """
    Create a prompt.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Permisos insuficientes")
    prompt_create.version = 1  # Always create a new version
    prompt = prompt_service.create(
        prompt_create=prompt_create,
        owner_id=current_user.id,
    )
    return PromptPublic.model_validate(prompt)


@router.patch(
    "/{id}/",
    response_model=PromptPublic,
)
def update_prompt(
    prompt_service: PromptServiceDep,
    current_user: CurrentUserDep,
    id: uuid.UUID,
    prompt_in: PromptUpdate,
) -> PromptPublic:
    """
    Update a prompt.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Permisos insuficientes")
    prompt = prompt_service.get_by_id(id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    prompt_in.version = prompt.version + 1
    prompt = prompt_service.update(prompt_update=prompt_in, id=id)
    return PromptPublic.model_validate(prompt)


@router.delete("/{id}/")
def delete_prompt(
    prompt_service: PromptServiceDep,
    current_user: CurrentUserDep,
    id: uuid.UUID,
) -> Message:
    """
    Delete a prompt.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Permisos insuficientes")
    prompt = prompt_service.get_by_id(id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    prompt_service.delete(id)
    return Message(message="Prompt eliminado correctamente")
