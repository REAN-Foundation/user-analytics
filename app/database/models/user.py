import json
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Float, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy_json import mutable_json_type
from app.database.base import Base
from sqlalchemy.sql import func

class User(Base):

    __tablename__ = "users"

    id                = Column(String(128), primary_key=True, index=True, nullable=False)
    TenantId          = Column(String(36), default=None, nullable=False)
    FirstName         = Column(String(128), default=None)
    LastName          = Column(String(128), default=None)
    Gender            = Column(String(16), default=None)
    Email             = Column(String(512), unique=True, default=None)
    PhoneCode         = Column(String(8), default=None)
    Phone             = Column(String(64), unique=True, default=None)
    LocationLongitude = Column(Float, default=None)
    LocationLatitude  = Column(Float, default=None)
    LastActive        = Column(DateTime(timezone=True), default=None)
    OnboardingSource  = Column(String(128), default=None)
    Role              = Column(String(128), default=None)
    Attributes        = Column(mutable_json_type(dbtype=JSONB, nested=True))
    TimezoneOffsetMin = Column(Integer, default=None, nullable=True)
    RegistrationDate  = Column(DateTime(timezone=True), default=None)
    CreatedAt         = Column(DateTime(timezone=True), server_default=func.now())
    UpdatedAt         = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    DeletedAt         = Column(DateTime(timezone=True), default=None)


    def __repr__(self):
        jsonStr = json.dumps(self.__dict__)
        return jsonStr
