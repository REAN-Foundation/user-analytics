import json
from sqlalchemy import Column, Enum, ForeignKey, String, DateTime, Text, func
from app.common.utils import generate_uuid4
from app.database.base import Base
from app.domain_types.enums.types import AnalysisType, Duration, Frequency

###############################################################################

class Filter(Base):

    __tablename__ = "filters"

    id           = Column(String(36), primary_key=True, index=True, default=generate_uuid4)
    Name         = Column(String(256))
    Description  = Column(String(1024), default=None, nullable=True)
    UserId       = Column(String(36), ForeignKey("users.id"), default=None, nullable=False)
    OwnerId      = Column(String(36), default=None, nullable=False)
    TenantId     = Column(String(36), default=None, nullable=False)
    AnalysisType = Column(Enum(AnalysisType), default=AnalysisType.active_users, nullable=False)
    Frequency    = Column(Enum(Frequency), default=Frequency.per_day, nullable=False)
    Duration     = Column(Enum(Duration), default=Duration.last_1_month, nullable=False)
    Filters      = Column(Text, default=None, nullable=True)
    CreatedAt    = Column(DateTime(timezone=True), server_default=func.now())
    UpdatedAt    = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        jsonStr = json.dumps(self.__dict__)
        return jsonStr
