from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, index=True)
    aggregation_id = Column(String, index=True)
    utctime = Column(String, index=True)
    type = Column(String, index=True)
    data = Column(String)

    @classmethod
    def create(cls, aggregation_id: str, type: str, data: str):
        d = datetime.utcnow()
        return cls(id=str(uuid4()), aggregation_id=aggregation_id, utctime=str(d), type=type, data=data)

