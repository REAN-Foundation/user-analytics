from datetime import datetime
from enum import Enum
from typing import Any, List, Optional
from pydantic import UUID4, BaseModel, Field
from app.domain_types.enums.types import EventActionType
from app.domain_types.schemas.base_types import BaseSearchFilter, BaseSearchResults

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

class UserEngagementMetrics(BaseModel):
    TenantId                    : UUID4    = Field(description="Tenant ID")
    TenantName                  : str      = Field(description="Tenant Name")
    StartDate                   : datetime = Field(description="Start date for analytics")
    EndDate                     : datetime = Field(description="End date for analytics")
    DailyActiveUsers            : any      = Field(description="Daily active users per day (DAU)")
    WeeklyActiveUsers           : any      = Field(description="Weekly active users per week (WAU)")
    MonthlyActiveUsers          : any      = Field(description="Monthly active users per month (MAU)")
    StickinessRate              : any      = Field(description="Ratio of DAU to MAU, showing user engagement and loyalty (DAU/MAU).")
    AverageSessionLengthHours   : any      = Field(description="Average session duration Hours")
    LoginFrequency              : any      = Field(description="Average number of sessions per user per day/week/month.")
    RetentionRate               : any      = Field(description="Percentage of users who return to the app after their first use (day 1, day 7, day 30).")
    MostCommonlyVisitedFeatures : any      = Field(description="Most common events performed by users")
    # MostCommonlyVisitedScreens  : any      = Field(description="Most common actions performed by users")

class FeatureEngagementMetrics(BaseModel):
    TenantId                     : UUID4          = Field(description="Tenant ID")
    TenantName                   : str            = Field(description="Tenant Name")
    Feature                      : str            = Field(description="Name of the feature")
    StartDate                    : datetime       = Field(description="Start date for analytics")
    EndDate                      : datetime       = Field(description="End date for analytics")
    FeatureAccessFrequency       : dict[str, int] = Field(description="Frequency of feature access daily/weekly/monthly")
    AverageFeatureAccessDuration : dict[str, int] = Field(description="Duration of feature access daily/weekly/monthly")
    FeatureEngagementRate        : dict[str, int] = Field(description="Percentage of active users engaging with each feature.")
    FeatureChurnRate             : dict[str, int] = Field(description="Percentage of users who stop using the feature after their first use.")
    FeatureRetentionRate         : dict[str, int] = Field(description="Percentage of users who return to the feature after their first use.")
    TaskCompletionRate           : dict[str, int] = Field(description="Percentage of users who complete a task using the feature.")
    TaskAbandonmentRate          : dict[str, int] = Field(description="Percentage of users who abandon a task using the feature.")
    FeatureDropOffRate           : dict[str, int] = Field(description="Percentage of users who drop off after using the feature.")
    AverageFeatureDropOffTime    : dict[str, int] = Field(description="Average time spent before drop off after using the feature.")
    FeatureDropOffPoints         : dict[str, int] = Field(description="Most common points where users drop off after using the feature.")


class UserEngagementMetricsResponse(BaseModel):
    TenantId     : Optional[UUID4]    = Field(description="Tenant ID")
    StartDate    : Optional[datetime] = Field(description="Start date for analytics")
    EndDate      : Optional[datetime] = Field(description="End date for analytics")
    AnalysisCode : Optional[str]      = Field(description="Unique code to identify the analysis")
    URL          : Optional[str]      = Field(description="URL to access the user engagement metrics data")
    JsonURL      : Optional[str]      = Field(description="URL to access the JSON formatted user engagement metrics data")
    ExcelURL     : Optional[str]      = Field(description="URL to access the Excel formatted user engagement metrics data")
    PDFURL       : Optional[str]      = Field(description="URL to access the PDF formatted user engagement metrics data")

class FeatureEngagementMetricsResponse(UserEngagementMetricsResponse):
    Feature : str = Field(description="Name of the feature")
