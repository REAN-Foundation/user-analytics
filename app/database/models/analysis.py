import json
from sqlalchemy import Column, ForeignKey, Enum, Integer, String, DateTime, Text, func, JSON
from app.common.utils import generate_uuid4
from app.database.base import Base
from app.domain_types.enums.types import EventActionType

###############################################################################

class Analysis(Base):

    __tablename__ = "analysis"

    id         = Column(String(36), primary_key=True, index=True, default=generate_uuid4)
    Code       = Column(String(36), default=None, index=True, nullable=False)
    TenantId   = Column(String(36), default=None, index=True, nullable=False)
    TenantName = Column(String(256), default=None, nullable=False)
    DateStr    = Column(String(64), default=None, nullable=False)
    StartDate  = Column(DateTime(timezone=True), default=None, nullable=False)
    EndDate    = Column(DateTime(timezone=True), default=None, nullable=False)
    Data       = Column(Text, default=None, nullable=True)
    JsonUrl    = Column(String(256), default=None, nullable=True)
    ExcelUrl   = Column(String(256), default=None, nullable=True)
    PdfUrl     = Column(String(256), default=None, nullable=True)
    Url        = Column(String(256), default=None, nullable=True)
    CreatedAt  = Column(DateTime(timezone=True), server_default=func.now())
    UpdatedAt  = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        jsonStr = json.dumps(self.__dict__)
        return jsonStr
