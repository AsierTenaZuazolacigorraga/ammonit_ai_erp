import asyncio
import time
import uuid
from time import sleep
from typing import Any

from app.api.deps import CurrentUser, SessionDep, WebSocketManager
from app.models import (
    Machine,
    MachineCreate,
    MachinePublic,
    MachinesPublic,
    MachineUpdate,
    Message,
)
from fastapi import (
    APIRouter,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
)
from sqlmodel import func, select

router = APIRouter(prefix="/machines", tags=["machines"])
ws_manager = WebSocketManager()


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


@router.get("/{machine_id}", response_model=MachinePublic)
def read_machine(
    session: SessionDep, current_user: CurrentUser, machine_id: uuid.UUID
) -> Any:
    """
    Get machine by ID.
    """
    machine = session.get(Machine, machine_id)
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


@router.put("/{machine_id}", response_model=MachinePublic)
def update_machine(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    machine_id: uuid.UUID,
    machine_in: MachineUpdate,
) -> Any:
    """
    Update an machine.
    """
    machine = session.get(Machine, machine_id)
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


# @router.websocket("/ws")
# async def websocket_endpoint(
#     websocket: WebSocket,
#     # session: SessionDep,
#     # current_user: CurrentUser,
# ):
#     # if not current_user and not session:
#     #     raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

#     print("pre-connect")
#     await ws_manager.connect(websocket)
#     try:
#         i = 0
#         while True:
#             i += 1
#             # data = await websocket.receive_text()
#             print("pre-send")
#             await ws_manager.send({"counter": i}, websocket)
#             print("post-send")
#             # await ws_manager.broadcast(f"Client #{current_user} says: {data}")
#             await asyncio.sleep(1)  # Increment and broadcast every 1 second

#     except WebSocketDisconnect:
#         print("pre-disconnect")
#         ws_manager.disconnect(websocket)
#         print("pre-send-broadcast")
#         await ws_manager.send_broadcast({"counter": -1})
#         # await ws_manager.broadcast(f"Client #{current_user} left the chat")
