import uuid
from typing import Any

from app.api.deps import CurrentUser, SessionDep
from app.models import (
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
def read_measurements(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve measurements.
    """

    # if current_user.is_superuser:
    #     count_statement = select(func.count()).select_from(Measurement)
    #     count = session.exec(count_statement).one()
    #     statement = select(Measurement).offset(skip).limit(limit)
    #     measurements = session.exec(statement).all()
    # else:
    #     count_statement = (
    #         select(func.count())
    #         .select_from(Measurement)
    #         .where(Measurement.owner_id == current_user.id)
    #     )
    #     count = session.exec(count_statement).one()
    #     statement = (
    #         select(Measurement)
    #         .where(Measurement.owner_id == current_user.id)
    #         .offset(skip)
    #         .limit(limit)
    #     )
    #     measurements = session.exec(statement).all()

    return MeasurementsPublic(data=measurements, count=count)


@router.get("/{id}", response_model=MeasurementPublic)
def read_measurement(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get measurement by ID.
    """
    measurement = session.get(Measurement, id)
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")
    if not current_user.is_superuser and (
        measurement.owner.owner_id != current_user.id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return measurement


@router.post("/", response_model=MeasurementPublic)
def create_measurement(
    *, session: SessionDep, current_user: CurrentUser, measurement_in: MeasurementCreate
) -> Any:
    """
    Create new measurement.
    """

    machine = read_machine(session, current_user, measurement_in.owner_id)
    measurement = Measurement.model_validate(
        measurement_in, update={"owner_id": machine.id}
    )
    session.add(measurement)
    session.commit()
    session.refresh(measurement)
    return measurement
