from enum import Enum

# These are commonly encountered event categories.
# Do not set this enum to database. Keep it as string.

# Event categories are broad categories of events.
# The application features are considered as event categories.

class EventCategory(str, Enum):
    UserAccount     = "user-account"
    LoginSession    = "login-session"
    AppScreenVisit  = "app-screen-visit"
    Medication      = "medication"
    Appointment     = "appointment"
    Symptoms        = "symptoms"
    Vitals          = "vitals"
    LabRecords      = "lab-records"
    Documents       = "documents"
    Careplan        = "careplan"
    CareplanTask    = "careplan-task"
    UserTask        = "user-task"
    Communication   = "communication"
    Notification    = "notification"
    Exercise        = "exercise"
    Nutrition       = "nutrition"
    WaterIntake     = "water-intake"
    Mood            = "mood"
    Sleep           = "sleep"
    Steps           = "steps"
    Device          = "device"
    Survey          = "survey"
    Assessment      = "assessment"
    DailyAssessment = "daily-assessment"
    Forms           = "forms"
    Goals           = "goals"
    Chatbot         = "chatbot"
    Reminders       = "reminders"
    Settings        = "settings"
    Feedback        = "feedback"
    Support         = "support"





