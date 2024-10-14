from enum import Enum

# Event subjects are somewhere between event categories and event types
# as far as granularity is considered.
# They are basically the 'subject' of the event.
# For example
# - if the event type is 'MedicationScheduleTaken' and
# - the event category is 'Medication'
# then the subject here is 'MedicationSchedule'

# Please note that - Event subjects are not always enumerated as below.
# They can be dynamic as well. For example screen-names.
# In such cases the event subject can be any string.

class EventSubject(str, Enum):

    UserAccount        = "user-account"
    LoginSession       = "login-session"
    Medication         = "medication"
    MedicationSchedule = "medication-schedule"
    UserTask           = "user-task"
    CareplanEnrollment = "careplan-enrollment"
    CareplanStop = "careplan-stop"
    VitalsCholesterol           = "vitals-cholesterol"
    VitalsPulse                 = "vitals-pulse"
    VitalsBodyTemperature       = "vitals-body-temperature"
    VitalsBloodPressure         = "vitals-blood-pressure"
    VitalsBloodGlucose          = "vitals-blood-glucose"
    VitalsBodyWeight            = "vitals-body-weight"
    VitalsBodyHeight            = "vitals-body-height"
    VitalsBloodOxygenSaturation = "vitals-blood-oxygen-saturation"
    VitalsRespiratoryRate       = "vitals-respiratory-rate"

    Symptom             = "symptom"
    SymptomHowDoYouFeel = "symptom-how-do-you-feel"

    Assessment            = "assessment"
    AssessmentQuestion    = "assessment-question"
    CareplanAssessment    = "careplan-assessment"
    DailyAssessment       = "daily-assessment"
    EnergyLevelAssessment = "energy-level-assessment"
    SymptomAssessment     = "symptom-assessment"
    SurveyAssessment      = "survey-assessment"
    FormAssessment        = "form-assessment"

    LabRecord  = "lab-record"
    Step       = "step"
    Sleep      = "sleep"
    Stand      = "stand",
    Nutrition  = "nutrition",
    Food       = "food",
    Mood       = "mood"
    Meditation = "meditation"
    Goal       = "goal"
    Exercise   = "exercise"
    Water      = "water"

    PhysicalActivity = "physical-activity"
