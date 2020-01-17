from json import dumps
from uuid import UUID

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_200_OK,
)

from db import Base, SessionLocal, engine
from dbmodels import Event, EventType, EventManager
from permission import CommandManager

Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/events")
async def get_events(aggregation_id: str = None, db: Session = Depends(get_db)):
    """GET list of events"""
    if aggregation_id is not None:
        events = db.query(Event).filter(Event.aggregation_id == aggregation_id).all()
    else:
        events = db.query(Event).all()
    return events or HTTP_404_NOT_FOUND


@app.get("/events/{id}")
async def get_event(id: UUID, db: Session = Depends(get_db)):
    """GET event by its id"""
    event = db.query(Event).filter(Event.id == str(id)).first()
    return event or HTTP_404_NOT_FOUND


class InPermission(BaseModel):
    name: str
    resource_type: str
    value: bool


async def create_permission_event(permission: InPermission, db: Session):
    event = CommandManager.create_permission(db, permission.name, permission.resource_type, permission.value)
    return event.aggregation_id


async def modify_permission(
    aggregation_id: UUID, permission: InPermission, event_type: EventType, db: Session
):
    event = CommandManager.update_permission(db, aggregation_id, permission.name, permission.resource_type, permission.value)
    return event.aggregation_id


async def delete_permission_event(
    aggregation_id: UUID, db: Session = Depends(get_db)
) -> UUID:
    event = CommandManager.delete_permission(db, aggregation_id)
    return event.aggregation_id


@app.post("/permissions", status_code=HTTP_201_CREATED)
async def create_permission(
    permission: InPermission, db: Session = Depends(get_db)
) -> UUID:

    return await create_permission_event(permission, db)


@app.patch("/permissions/{id}", status_code=HTTP_200_OK)
async def update_permission(
    id: UUID, permission: InPermission, db: Session = Depends(get_db)
) -> UUID:

    return await modify_permission(id, permission, EventType.UPDATED, db)


@app.delete("/permissions/{id}", status_code=HTTP_200_OK)
async def delete_permission(
    id: UUID, db: Session = Depends(get_db)
) -> UUID:

    return await delete_permission_event(id, db)


@app.get("/permissions", status_code=HTTP_201_CREATED)
async def get_permission(db: Session = Depends(get_db)) -> str:
    return db.query(Event).all()


@app.get("/permissions/{id}", status_code=HTTP_200_OK)
async def get_permission(id: UUID, db: Session = Depends(get_db)) -> str:
    events = db.query(Event).filter(Event.aggregation_id == str(id)).all()
    return events
