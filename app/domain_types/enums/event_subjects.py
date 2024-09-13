from enum import Enum

# Event subjects are somewhere between event categories and event types
# as far as granularity is considered.
# They are basically the 'subject' of the event.
# For example,
# - if the event type is 'MedicationScheduleTaken' and
# - the event category is 'Medication',
# then the subject here is 'MedicationSchedule'

# Please note that - Event subjects are not always enumerated as below.
# They can be dynamic as well. For example, screen-names.
# In such cases, the event subject can be any string.

class EventSubject(str, Enum):
    Signup             = "signup"
    Profile            = "profile"
    Login              = "login"
    Medication         = "medication"
    MedicationSchedule = "medication-schedule"
    LabRecord          = "lab-record"
    Symptom            = "symptom"
    Vital              = "vital"
    Assessment         = "assessment"
    Careplan           = "careplan"
    CareplanTask       = "careplan-task"
    UserTask           = "user-task"
