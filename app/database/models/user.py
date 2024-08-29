import json
from sqlalchemy import Column, DateTime, Integer, String, Float, Text
from app.database.base import Base
from sqlalchemy.sql import func

###############################################################################

class User(Base):

    __tablename__ = "users"

    id                = Column(String(36), primary_key=True, index=True)
    TenantId          = Column(String(36), nullable=False)
    BirthDate         = Column(DateTime(timezone=False), default=None)
    Gender            = Column(String(32), default=None)
    LocationLongitude = Column(Float, default=None)
    LocationLatitude  = Column(Float, default=None)
    LastActive        = Column(DateTime(timezone=True), default=None)
    OnboardingSource  = Column(String(128), default=None)
    Role              = Column(String(128), default=None)
    Attributes        = Column(Text, default=None, nullable=True)
    TimezoneOffsetMin = Column(Integer, default=None, nullable=True)
    RegistrationDate  = Column(DateTime(timezone=True), default=None)
    CreatedAt         = Column(DateTime(timezone=True), server_default=func.now())
    UpdatedAt         = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    DeletedAt         = Column(DateTime(timezone=True), default=None)


    def __repr__(self):
        jsonStr = json.dumps(self.__dict__)
        return jsonStr
