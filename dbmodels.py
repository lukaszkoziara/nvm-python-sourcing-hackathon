from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, String

from db import Base


class EventType(str, Enum):
    CREATED = 'CREATED'
    UPDATED = 'UPDATED'
    DELETED = 'DELETED'


class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, index=True)
    aggregation_id = Column(String, index=True)
    utctime = Column(String, index=True)
    type = Column(String, index=True)  # CREATED | UPDATED | DELETED
    data = Column(String)

    @classmethod
    def create(cls, type: EventType, data: str) -> 'Event':
        utctime = str(datetime.utcnow())
        id_ = str(uuid4())
        aggregation_id = str(uuid4())
        return cls(id=id_, aggregation_id=aggregation_id, utctime=utctime, type=type, data=data)

    @classmethod
    def exists(cls, aggregation_id, db) -> bool:
        return bool(db.query(cls).filter(aggregation_id == aggregation_id).first())


class EventManager:
    def __init__(self, db):
        self.db = db

    def can_insert(self, event: Event):
        event_type = EventType[event.type]
        aggregation_id = event.aggregation_id
        if event_type is EventType.CREATED:
            return not self._is_created(aggregation_id)
        else:
            return self._is_created(aggregation_id) and not self._is_deleted(aggregation_id)

    def _is_created(self, aggregation_id: str) -> bool:
        return bool(self.db.query(Event).filter(Event.aggregation_id == aggregation_id).first())

    def _is_deleted(self, aggregation_id: str) -> bool:
        return bool(self.db.query(Event).filter(
            (Event.aggregation_id == aggregation_id) & (Event.type == EventType.DELETED.value)
        ).first())
