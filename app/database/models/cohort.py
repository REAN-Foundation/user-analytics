import json
from sqlalchemy import Column, String, DateTime, Text, func
from app.common.utils import generate_uuid4
from app.database.base import Base

class Cohort(Base):

    __tablename__ = "cohorts"

    id                   = Column(String(36), primary_key=True, index=True, default=generate_uuid4)
    Name                 = Column(String(256), nullable=False)
    Description          = Column(String(1024), nullable=True)
    TenantId             = Column(String(36), default=None, nullable=False)
    OwnerId              = Column(String(36), default=None, nullable=False)
    Attributes           = Column(Text, default=None, nullable=True)
    CreatedAt            = Column(DateTime(timezone=True), server_default=func.now())
    UpdatedAt            = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        jsonStr = json.dumps(self.__dict__)
        return jsonStr

