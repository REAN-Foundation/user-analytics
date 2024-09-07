import json
from sqlalchemy import Column, ForeignKey, Enum, Integer, String, DateTime, Text, func, JSON
from app.common.utils import generate_uuid4
from app.database.base import Base
from app.domain_types.enums.types import EventActionType

###############################################################################

class Event(Base):

    __tablename__ = "events"

    id                          = Column(String(36), primary_key=True, index=True, default=generate_uuid4)
    UserId                      = Column(String(36), default=None, index=True, nullable=False)
    TenantId                    = Column(String(36), default=None, index=True, nullable=False)
    SessionId                   = Column(String(36), default=None, nullable=True)
    ResourceId                  = Column(String(36), default=None, nullable=True)
    ResourceType                = Column(String(256), default=None, nullable=True)
    SourceName                  = Column(String(256), default=None, nullable=False)
    SourceVersion               = Column(String(256), default=None, nullable=True)
    EventName                   = Column(String(256), default=None, nullable=False)
    EventSubject                = Column(String(256), default=None, nullable=True)
    EventCategory               = Column(String(256), default=None, nullable=False)
    ActionType                  = Column(String(128), default=None, nullable=False)
    ActionStatement             = Column(String(512), default=None, nullable=True)
    Attributes                  = Column(Text, default=None, nullable=True)
    Timestamp                   = Column(DateTime(timezone=True), server_default=func.now())
    DaysSinceRegistration       = Column(Integer, nullable=False)
    TimeOffsetSinceRegistration = Column(Integer, nullable=False)
    CreatedAt                   = Column(DateTime(timezone=True), server_default=func.now())
    UpdatedAt                   = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        jsonStr = json.dumps(self.__dict__)
        return jsonStr
