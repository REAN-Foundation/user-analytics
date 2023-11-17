import json
from sqlalchemy import Column, String, DateTime, func
from app.common.utils import generate_uuid4
from app.database.base import Base

class CohortUser(Base):

    __tablename__ = "cohort_users"

    id                   = Column(String(36), primary_key=True, index=True, default=generate_uuid4)
    TenantId             = Column(String(36), default=None, nullable=True)
    CohortId             = Column(String(36), default=None, nullable=False)
    UserId               = Column(String(36), default=None, nullable=False)
    CreatedAt            = Column(DateTime(timezone=True), server_default=func.now())
    UpdatedAt            = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        jsonStr = json.dumps(self.__dict__)
        return jsonStr

