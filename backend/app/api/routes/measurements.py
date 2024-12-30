import uuid
from typing import Any

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Machine,
    Measurement,
    MeasurementCreate,
    MeasurementPublic,
    MeasurementsPublic,
    MeasurementUpdate,
    Message,
)
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from .machines import read_machine

router = APIRouter(prefix="/measurements", tags=["measurements"])


@router.get("/", response_model=MeasurementsPublic)
def read_latest_measurements(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Retrieve measurements.
    """

    # if not current_user.is_superuser and (
    #     measurement.owner.owner_id != current_user.id
    # ):
    #     raise HTTPException(status_code=400, detail="Not enough permissions")

    # if current_user.is_superuser:
    #     count_statement = select(func.count()).select_from(Measurement)
    #     count = session.exec(count_statement).one()
    #     statement = select(Measurement).offset(skip).limit(limit)
    #     measurements = session.exec(statement).all()
    # else:
    #     count_statement = (
    #         select(func.count())
    #         .select_from(Measurement)
    #         .join(Machine, Measurement.owner_id == Machine.id)
    #         .where(Machine.owner_id == current_user.id)
    #     )
    #     count = session.exec(count_statement).one()
    #     statement = (
    #         select(Measurement)
    #         .join(Machine, Measurement.owner_id == Machine.id)
    #         .where(Machine.owner_id == current_user.id)
    #         .offset(skip)
    #         .limit(limit)
    #     )
    #     measurements = session.exec(statement).all()

    measurements = []
    count = 0

    return MeasurementsPublic(data=measurements, count=count)


@router.get("/{machine_id}/{measurement_id}", response_model=MeasurementPublic)
def read_measurement(
    session: SessionDep,
    current_user: CurrentUser,
    machine_id: uuid.UUID,
    measurement_id: uuid.UUID,
) -> Any:
    """
    Get measurement by ID.
    """
    machine = read_machine(session, current_user, machine_id)
    measurement = session.get(Measurement, measurement_id)
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")
    if not machine.id != measurement.owner_id:
        raise HTTPException(
            status_code=400, detail="Measurement not related to machine"
        )
    return measurement


@router.post("/{machine_id}", response_model=MeasurementPublic)
def create_measurement(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    measurement_in: MeasurementCreate,
    machine_id: uuid.UUID
) -> Any:
    """
    Create new measurement.
    """

    machine = read_machine(session, current_user, machine_id)
    measurement = Measurement.model_validate(
        measurement_in, update={"owner_id": machine.id}
    )
    session.add(measurement)
    session.commit()
    session.refresh(measurement)
    return measurement
