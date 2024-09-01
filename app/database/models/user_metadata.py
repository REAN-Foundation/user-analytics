import json
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Float, Text
from app.database.base import Base
from sqlalchemy.sql import func

###############################################################################

class UserMetadata(Base):

    __tablename__ = "user_metadata"

    UserId            = Column(String(36), primary_key=True, index=True)
    BirthDate         = Column(DateTime(timezone=False), default=None)
    Gender            = Column(String(32), default=None)
    LocationLongitude = Column(Float, default=None)
    LocationLatitude  = Column(Float, default=None)
    OnboardingSource  = Column(String(128), default=None)
    Role              = Column(String(128), default=None)
    Attributes        = Column(Text, default=None)
    Ethnicity         = Column(String(128), default=None)
    Race              = Column(String(128), default=None)
    HealthSystem      = Column(String(128), default=None)
    Hospital          = Column(String(128), default=None)
    IsCareGiver       = Column(Boolean, default=None)
    MajorDiagnosis    = Column(String(128), default=None)
    Smoker            = Column(Boolean, default=None)
    Alcoholic         = Column(Boolean, default=None)
    SubstanceAbuser   = Column(Boolean, default=None)


    def __repr__(self):
        jsonStr = json.dumps(self.__dict__)
        return jsonStr
