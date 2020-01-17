from json import dumps
from uuid import UUID

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from db import Base, SessionLocal, engine
from dbmodels import Event, EventType, EventManager

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
async def get_events(aggregation_id: str = None, db: Session = Depends(get_db)):
    """GET list of events"""
    if aggregation_id is not None:
        events = db.query(Event).filter(Event.aggregation_id == aggregation_id).all()
    else:
        events = db.query(Event).all()
    return events or HTTP_404_NOT_FOUND


@app.get('/events/{id}')
async def get_event(id: UUID, db: Session = Depends(get_db)):
    """GET event by its id"""
    event = db.query(Event).filter(Event.id == str(id)).first()
    return event or HTTP_404_NOT_FOUND


class InPermission(BaseModel):
    name: str
    resource_type: str
    value: bool


async def create_event(permission: InPermission, event_type: EventType, db: Session):
    event = Event.create(
        aggregation_id=permission.name,
        type=event_type,
        data=dumps({'resource_type': permission.resource_type, 'value': permission.value}))

    if not EventManager(db).can_insert(event):
        return HTTP_409_CONFLICT

    db.add(event)
    db.commit()
    return event.id


@app.post('/permissions', status_code=HTTP_201_CREATED)
async def create_permission(permission: InPermission,
                            db: Session = Depends(get_db)) -> str:
    return await create_event(permission, EventType.CREATED, db)


@app.patch('/permissions', status_code=HTTP_201_CREATED)
async def update_permission(permission: InPermission,
                            db: Session = Depends(get_db)) -> str:
    return await create_event(permission, EventType.UPDATED, db)


@app.delete('/permissions', status_code=HTTP_201_CREATED)
async def delete_permission(permission: InPermission,
                            db: Session = Depends(get_db)) -> str:
    return await create_event(permission, EventType.DELETED, db)


@app.get('/permissions', status_code=HTTP_201_CREATED)
async def get_permission(db: Session = Depends(get_db)) -> str:
    return db.query(Event).all()


@app.get('/permissions/{id}', status_code=HTTP_201_CREATED)
async def get_permission(id: str, db: Session = Depends(get_db)) -> str:
    events = db.query(Event).filter(Event.aggregation_id == id).all()
    return events
