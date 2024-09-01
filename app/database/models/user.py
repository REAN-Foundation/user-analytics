import json
from sqlalchemy import Column, DateTime, Integer, String, Float, Text
from app.database.base import Base
from sqlalchemy.sql import func

###############################################################################

class User(Base):

    __tablename__ = "users"

    id                = Column(String(36), primary_key=True, index=True)
    TenantId          = Column(String(36), nullable=False)
    RoleId            = Column(Integer, nullable=True, default=None)
    LastActive        = Column(DateTime(timezone=True), default=None)
    OnboardingSource  = Column(String(128), default=None)
    TimezoneOffsetMin = Column(Integer, default=None, nullable=True)
    RegistrationDate  = Column(DateTime(timezone=True), default=None)
    DeletedAt         = Column(DateTime(timezone=True), default=None)

    def __repr__(self):
        jsonStr = json.dumps(self.__dict__)
        return jsonStr
