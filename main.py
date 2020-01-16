from enum import Enum
from json import dumps

from fastapi import FastAPI, Depends
from pydantic import BaseModel

from sqlalchemy.orm import Session

from db import Base, SessionLocal, engine
from dbmodels import Event


Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get('/events')
async def get_events():
    """GET list of all events"""
    return []


@app.get('/events/{_id}')
async def get_event(id: int):
    """GET event by its id"""
    return {'id': id}


class EventType(str, Enum):
    CREATED = 'CREATED'
    UPDATED = 'UPDATED'
    DELETED = 'DELETED'


class InPermission(BaseModel):
    name: str
    resource_type: str
    value: bool


@app.post('/permissions')
async def create_permission(permission: InPermission,
                            db: Session = Depends(get_db)) -> str:

    event = Event.create(
        aggregation_id=permission.name,
        type=EventType.CREATED,
        data=dumps({'resource_type': permission.resource_type, 'value': permission.value}))
    db.add(event)
    db.commit()
    return event.id
