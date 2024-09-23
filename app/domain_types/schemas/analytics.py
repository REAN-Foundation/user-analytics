from datetime import date, datetime
from enum import Enum
import json
from typing import Any, List, Optional

from pydantic import UUID4, BaseModel, Field

from app.domain_types.enums.types import EventActionType
from app.domain_types.schemas.base_types import (BaseSearchFilter,
                                                 BaseSearchResults)

###############################################################################

class AgeGroup(str, Enum):
    AGE_0_18    = "0-18"
    AGE_19_30   = "19-30"
    AGE_31_45   = "31-45"
    AGE_46_60   = "46-60"
    AGE_61_75   = "61-75"
    AGE_76_90   = "76-90"
    AGE_91_105  = "91-105"
    AGE_106_120 = "106-120"
    UNKNOWN     = "Unknown"


class Demographics(BaseModel):
    AgeGroups                       : list = Field(description="Age group distribution by user counts")
    GenderGroups                    : list = Field(description="Gender group distribution by user counts")
    LocationGroups                  : list = Field(description="Location group distribution by user counts")
    EthnicityGroups                 : list = Field(description="Ethnicity group distribution by user counts")
    RaceGroups                      : list = Field(description="Race group distribution by user counts")
    HealthSystemDistribution        : list = Field(description="Health system group distribution by user counts")
    HospitalDistribution            : list = Field(description="Hospital group distribution by user counts")
    SurvivorOrCareGiverDistribution : list = Field(description="Survivor or Caregiver group distribution by user counts")

class BasicAnalyticsStatistics(BaseModel):
    TenantId                     : UUID4|None        = Field(description="Tenant ID")
    TenantName                   : str               = Field(description="Tenant Name")
    StartDate                    : datetime          = Field(description="Start date for analytics")
    EndDate                      : datetime          = Field(description="End date for analytics")
    TotalUsers                   : int               = Field(description="Total number of users")
    TotalPatients                : int               = Field(description="Total number of patients")
    TotalActivePatients          : int               = Field(description="Total number of active patients")
    # TotalDeletedPatients         : int               = Field(description="Total number of inactive patients")
    PatientRegistrationHistory   : list|None         = Field(description="User registration history")
    PatientDeregistrationHistory : list|None         = Field(description="User deregistration history")
    PatientDemographics          : Demographics|None = Field(description="User demographics")

class GenericEngagementMetrics(BaseModel):
      TenantId                        : UUID4|None     = Field(description="Tenant ID")
      TenantName                      : str            = Field(description="Tenant Name")
      StartDate                       : str|None       = Field(description="Start date for analytics")
      EndDate                         : str|None       = Field(description="End date for analytics")
      DailyActiveUsers                : list|dict|None = Field(description="Daily active users per day (DAU)")
      WeeklyActiveUsers               : list|dict|None = Field(description="Weekly active users per week (WAU)")
      MonthlyActiveUsers              : list|dict|None = Field(description="Monthly active users per month (MAU)")
      StickinessRatio                 : list|dict|None = Field(description="Ratio of DAU to MAU, showing user engagement and loyalty (DAU/MAU).")
      AverageSessionLengthMinutes     : float|None     = Field(description="Average session duration in minutes.")
      LoginFrequency                  : list|dict|None = Field(description="Average number of sessions per user per day/week/month.")
      RetentionRateOnSpecificDays     : list|dict|None = Field(description="Percentage of users who return to the app after their first use (day 1, day 7, day 30).")
      RetentionRateInSpecificIntervals: list|dict|None = Field(description="Percentage of users who return to the app after their first use (day 1, day 7, day 30).")
      MostCommonlyVisitedFeatures     : list|dict|None = Field(description="Most common events performed by users")
      MostCommonlyVisitedScreens      : list|dict|None = Field(description="Most common screens visited by users")

class FeatureEngagementMetrics(BaseModel):
    Feature                          : str            = Field(description="Name of the feature")
    TenantId                         : UUID4|None     = Field(description="Tenant ID")
    TenantName                       : str|None       = Field(description="Tenant Name")
    StartDate                        : datetime|None  = Field(description="Start date for analytics")
    EndDate                          : datetime|None  = Field(description="End date for analytics")
    AccessFrequency                  : list|dict|None = Field(description="Frequency of feature access daily/weekly/monthly")
    AverageUsageDurationMinutes      : float|None     = Field(description="Duration of feature usage")
    EngagementRate                   : list|dict|None = Field(description="Percentage of active users engaging with each feature.")
    RetentionRateOnSpecificDays      : list|dict|None = Field(description="Percentage of users who return to the feature after their first use.")
    RetentionRateInSpecificIntervals : list|dict|None = Field(description="Percentage of users who return to the feature after their first use.")
    DropOffPoints                    : list|dict|None = Field(description="Most common points where users drop off after using the feature.")

class EngagementMetrics(BaseModel):
      TenantId        : UUID4|None                          = Field(description="Tenant ID")
      TenantName      : str|None                            = Field(description="Tenant Name")
      StartDate       : datetime                            = Field(description="Start date for analytics")
      EndDate         : datetime                            = Field(description="End date for analytics")
      BasicStatistics : BasicAnalyticsStatistics|None       = Field(description="Basic analytics statistics")
      GenericMetrics  : GenericEngagementMetrics|None       = Field(description="User engagement metrics")
      FeatureMetrics  : List[FeatureEngagementMetrics]|None = Field(description="Feature engagement metrics")

###############################################################################

class CalculateMetricsResponse(BaseModel):
    TenantId     : Optional[UUID4|str|None]    = Field(description="Tenant ID")
    RoleId       : Optional[int|str|None]      = Field(description="Role ID")
    StartDate    : Optional[datetime|str|None] = Field(description="Start date for analytics")
    EndDate      : Optional[datetime|str|None] = Field(description="End date for analytics")
    AnalysisCode : Optional[str]               = Field(description="Unique code to identify the analysis")
    URL          : Optional[str]               = Field(description="URL to access the user engagement metrics data")
    JsonURL      : Optional[str]               = Field(description="URL to access the JSON formatted user engagement metrics data")
    ExcelURL     : Optional[str]               = Field(description="URL to access the Excel formatted user engagement metrics data")
    PdfURL       : Optional[str]               = Field(description="URL to access the PDF formatted user engagement metrics data")

class AnalyticsFilters(BaseModel):
    TenantId   : Optional[UUID4|None] = Field(description="Tenant ID", default=None)
    TenantName : Optional[str|None]   = Field(description="Tenant Name", default=None)
    RoleId     : Optional[int|None]   = Field(description="Role ID", default=None)
    Source     : Optional[str|None]   = Field(description="Source application of the event", default=None)
    StartDate  : Optional[date|None]  = Field(description="Start date for events", default=None)
    EndDate    : Optional[date|None]  = Field(description="End date for events", default=None)

    def __repr__(self):
        jsonStr = json.dumps(self.__dict__)
        return jsonStr
