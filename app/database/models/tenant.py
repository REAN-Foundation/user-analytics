import json
from sqlalchemy import Column, DateTime, Integer, String, Float, Text
from app.database.base import Base
from sqlalchemy.sql import func

###############################################################################

class Tenant(Base):

    __tablename__ = "tenants"

    id                = Column(String(36), primary_key=True, index=True)
    TenantName        = Column(String(128), default=None)
    TenantCode        = Column(String(128), default=None)
    RegistrationDate  = Column(DateTime(timezone=True), default=None)
    CreatedAt         = Column(DateTime(timezone=True), server_default=func.now())
    UpdatedAt         = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    DeletedAt         = Column(DateTime(timezone=True), default=None)


    def __repr__(self):
        jsonStr = json.dumps(self.__dict__)
        return jsonStr
