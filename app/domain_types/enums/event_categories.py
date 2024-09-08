from enum import Enum

# These are commonly encountered event categories.
# The application features are categorized into these event categories.
# But do not set this enum to database. Keep it as string.

class EventCategory(str, Enum):
    Signup          = "signup"
    Profile         = "profile"
    Login           = "login"
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





