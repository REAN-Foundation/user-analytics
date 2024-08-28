import json
from sqlalchemy import Column, Integer, String, DateTime, Text, func
from app.common.utils import generate_uuid4
from app.database.base import Base

###############################################################################

class UserMilestone(Base):

    __tablename__ = "user_milestones"

    id                          = Column(String(36), primary_key=True, index=True, default=generate_uuid4)
    UserId                      = Column(String(36), default=None, nullable=False)
    TenantId                    = Column(String(36), default=None, nullable=False)
    MilestoneName               = Column(String(256), default=None, nullable=False)
    MilestoneCategory           = Column(String(256), default=None, nullable=True)
    Attributes                  = Column(Text, default=None, nullable=True)
    Timestamp                   = Column(DateTime(timezone=True), server_default=func.now())
    DaysSinceRegistration       = Column(Integer, nullable=False)
    TimeOffsetSinceRegistration = Column(Integer, nullable=False)
    CreatedAt                   = Column(DateTime(timezone=True), server_default=func.now())
    UpdatedAt                   = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        jsonStr = json.dumps(self.__dict__)
        return jsonStr
