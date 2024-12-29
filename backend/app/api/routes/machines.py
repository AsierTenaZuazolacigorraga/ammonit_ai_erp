import uuid
from typing import Any

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Machine,
    MachineCreate,
    MachinePublic,
    MachinesPublic,
    MachineUpdate,
    Message,
)
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

router = APIRouter(prefix="/machines", tags=["machines"])


@router.get("/", response_model=MachinesPublic)
def read_machines(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve machines.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Machine)
        count = session.exec(count_statement).one()
        statement = select(Machine).offset(skip).limit(limit)
        machines = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Machine)
            .where(Machine.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Machine)
            .where(Machine.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        machines = session.exec(statement).all()

    return MachinesPublic(data=machines, count=count)


@router.get("/{id}", response_model=MachinePublic)
def read_machine(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get machine by ID.
    """
    machine = session.get(Machine, id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    if not current_user.is_superuser and (machine.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return machine


@router.post("/", response_model=MachinePublic)
def create_machine(
    *, session: SessionDep, current_user: CurrentUser, machine_in: MachineCreate
) -> Any:
    """
    Create new machine.
    """
    machine = Machine.model_validate(machine_in, update={"owner_id": current_user.id})
    session.add(machine)
    session.commit()
    session.refresh(machine)
    return machine


@router.put("/{id}", response_model=MachinePublic)
def update_machine(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    machine_in: MachineUpdate,
) -> Any:
    """
    Update an machine.
    """
    machine = session.get(Machine, id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    if not current_user.is_superuser and (machine.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = machine_in.model_dump(exclude_unset=True)
    machine.sqlmodel_update(update_dict)
    session.add(machine)
    session.commit()
    session.refresh(machine)
    return machine


@router.delete("/{id}")
def delete_machine(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an machine.
    """
    machine = session.get(Machine, id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    if not current_user.is_superuser and (machine.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(machine)
    session.commit()
    return Message(message="Machine deleted successfully")
