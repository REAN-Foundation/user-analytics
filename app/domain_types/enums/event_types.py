from enum import Enum

# These are commonly encountered event types.
# But do not set this enum to database. Keep it as string.

class EventType(str, Enum):
    # User events
    UserSignup = "user-sign-up"
    UserLogin = "user-login"
    UserLogout = "user-logout"
    UserPasswordChange = "user-password-change"
    UserPasswordReset = "user-password-reset"
    UserEmailChange = "user-email-change"
    UserPhoneChange = "user-phone-change"
    UserMetadataUpdate = "user-metadata-update"
    UserDelete = "user-delete"
    # User medication events
    MedicationCreate = "medication-create"
    MedicationUpdate = "medication-update"
    MedicationDelete = "medication-delete"
    # User medication schedule events
    MedicationScheduleTaken = "medication-schedule-taken"
    MedicationScheduleMissed = "medication-schedule-missed"


