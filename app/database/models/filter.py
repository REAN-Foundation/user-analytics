import json
import uuid
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, func, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy_json import mutable_json_type
from app.common.utils import generate_uuid4
from app.database.base import Base

class Filter(Base):

    __tablename__ = "filters"

    id               = Column(String(36), primary_key=True, index=True, default=generate_uuid4)
    Name             = Column(String(256))
    Description      = Column(String(1024), default=None, nullable=True)
    UserId           = Column(String(36), ForeignKey("users.id"), default=None, nullable=False)
    OwnerId          = Column(String(36), default=None, nullable=False)
    TenantId         = Column(String(36), default=None, nullable=False)
    Filters          = Column(mutable_json_type(dbtype=JSONB, nested=True))
    CreatedAt        = Column(DateTime(timezone=True), server_default=func.now())
    UpdatedAt        = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        jsonStr = json.dumps(self.__dict__)
        return jsonStr
