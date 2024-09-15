from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.assessments.assessment_events_synchronizer import AssessmentEventsSynchronizer
from app.modules.data_sync.careplans.careplan_events_synchronizer import CareplanEventsSynchronizer
from app.modules.data_sync.goals.goal_events_synchronizer import GoalEventsSynchronizer
from app.modules.data_sync.lab_records.lab_record_events_synchonizer import LabRecordEventsSynchronizer
from app.modules.data_sync.meditations.meditation_events_synchronizer import MeditationEventsSynchronizer
from app.modules.data_sync.mood.mood_events_synchronizer import MoodEventsSynchronizer
from app.modules.data_sync.nutrition.nutrition_events_synchronizer import NutritionEventsSynchronizer
from app.modules.data_sync.sleep.sleep_events_synchronizer import SleepEventsSynchronizer
from app.modules.data_sync.stand.stand_events_synchronizer import StandEventsSynchronizer
from app.modules.data_sync.steps.step_events_synchronizer import StepEventsSynchronizer
from app.modules.data_sync.symptoms.symptom_events_synchronizer import SymptomEventsSynchronizer
from app.modules.data_sync.user_tasks.user_task_events_synchronizer import UserTaskEventsSynchronizer
from app.modules.data_sync.vitals.blood_glucose_events_synchronizer import BloodGlucoseEventsSynchronizer
from app.modules.data_sync.vitals.cholesterol_events_synchronizer import CholesterolEventsSynchronizer
from app.modules.data_sync.vitals.oxygen_saturation_events_synchronizer import OxygenSaturationEventsSynchronizer
from app.modules.data_sync.vitals.blood_pressure_events_synchronizer import BloodPressureEventsSynchronizer
from app.modules.data_sync.vitals.body_height_events_synchronizer import BodyHeightEventsSynchronizer
from app.modules.data_sync.vitals.body_temperature_events_synchronizer import BodyTemperatureEventsSynchronizer
from app.modules.data_sync.vitals.body_weight_events_synchronizer import BodyWeightEventsSynchronizer
from app.modules.data_sync.data_synchronizer import DataSynchronizer
from app.modules.data_sync.login_events_synchonizer import LoginEventsSynchronizer
from app.modules.data_sync.medications.medication_events_synchronizer import MedicationEventsSynchronizer
from app.modules.data_sync.vitals.pulse_events_synchronizer import PulseEventsSynchronizer
from app.telemetry.tracing import trace_span
import asyncio

###############################################################################

@trace_span("handler: sync_users")
def sync_users_():
    try:
        # Please note that there are users with patient role
        # but there is no corresponding entry in the patients table
        # So such users are not synched.
        DataSynchronizer.sync_users()
    except Exception as e:
        print(e)

@trace_span("handler: sync_user_login_session_events")
def sync_user_login_session_events_():
    try:
        LoginEventsSynchronizer.sync_user_login_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_medication_events")
def sync_medication_events_(filters: DataSyncSearchFilter):
    try:
        MedicationEventsSynchronizer.sync_medication_create_events(filters)
        MedicationEventsSynchronizer.sync_medication_delete_events(filters)
        MedicationEventsSynchronizer.sync_medication_schedule_taken_events(filters)
        MedicationEventsSynchronizer.sync_medication_schedule_missed_events(filters)
    except Exception as e:
        print(e)

@trace_span("handler: sync_symptom_events")
def sync_symptom_events_(filters: DataSyncSearchFilter):
    try:
        print("Starting symptom events synchronization...")
        SymptomEventsSynchronizer.sync_symptom_create_events(filters),
        SymptomEventsSynchronizer.sync_symptom_update_events(filters),
        SymptomEventsSynchronizer.sync_symptom_delete_events(filters)

        print("Symptom events synchronization completed.")
    except Exception as e:
        print(e)

@trace_span("handler: sync_lab_record_events")
def sync_lab_record_events_(filters: DataSyncSearchFilter):
    try:
        print("Starting lab record events synchronization...")
        LabRecordEventsSynchronizer.sync_lab_record_create_events(filters),
        LabRecordEventsSynchronizer.sync_lab_record_delete_events(filters)
        print("Lab record events synchronization completed.")
    except Exception as e:
        print(e)

@trace_span("handler: sync_biometric_events")
def sync_biometric_events_(filters: DataSyncSearchFilter):
    try:
        print("Starting biometric events synchronization...")
        PulseEventsSynchronizer.sync_pulse_create_events(filters)
        PulseEventsSynchronizer.sync_pulse_delete_events(filters)
        BodyWeightEventsSynchronizer.sync_body_weight_create_events(filters)
        BodyWeightEventsSynchronizer.sync_body_weight_delete_events(filters)
        BodyTemperatureEventsSynchronizer.sync_body_temperature_create_events(filters)
        BodyTemperatureEventsSynchronizer.sync_body_temperature_delete_events(filters)
        BodyHeightEventsSynchronizer.sync_body_height_create_events(filters)
        BodyHeightEventsSynchronizer.sync_body_height_delete_events(filters)
        BloodPressureEventsSynchronizer.sync_blood_pressure_create_events(filters)
        BloodPressureEventsSynchronizer.sync_blood_pressure_delete_events(filters)
        OxygenSaturationEventsSynchronizer.sync_oxygen_saturation_create_events(filters)
        OxygenSaturationEventsSynchronizer.sync_oxygen_saturation_delete_events(filters)
        BloodGlucoseEventsSynchronizer.sync_blood_glucose_create_events(filters)
        BloodGlucoseEventsSynchronizer.sync_blood_glucose_delete_events(filters)
        CholesterolEventsSynchronizer.sync_cholesterol_create_events(filters)
        CholesterolEventsSynchronizer.sync_cholesterol_delete_events(filters)
        print("Biometric events synchronization completed.")
    except Exception as e:
        print(e)

@trace_span("handler: sync_assessment_events")
def sync_assessment_events_(filters: DataSyncSearchFilter):
    try:
        print("Starting assessment events synchronization...")
        AssessmentEventsSynchronizer.sync_assessment_create_events(filters)
        AssessmentEventsSynchronizer.sync_assessment_delete_events(filters)
        AssessmentEventsSynchronizer.sync_assessment_start_events(filters)
        AssessmentEventsSynchronizer.sync_assessment_complete_events(filters)
        AssessmentEventsSynchronizer.sync_assessment_question_answered_events(filters)
        print("Assessment events synchronization completed.")
    except Exception as e:
        print(e)

@trace_span("handler: sync_careplan_events")
def sync_careplan_events_(filters: DataSyncSearchFilter):
    try:
        print("Starting careplan events synchronization...")
        CareplanEventsSynchronizer.sync_careplan_enroll_events(filters)
        # CareplanEventsSynchronizer.sync_careplan_start_events(filters)
        # CareplanEventsSynchronizer.sync_careplan_stop_events(filters)
        CareplanEventsSynchronizer.sync_careplan_complete_events(filters)
        # CareplanEventsSynchronizer.sync_careplan_task_start_events(filters)
        # CareplanEventsSynchronizer.sync_careplan_task_complete_events(filters)
        CareplanEventsSynchronizer.sync_careplan_stop_events(filters)
        print("Careplan events synchronization completed.")
    except Exception as e:
        print(e)

@trace_span("handler: sync_user_task_events")
def sync_user_task_events_(filters: DataSyncSearchFilter):
    try:
        print("Starting user task events synchronization...")
        UserTaskEventsSynchronizer.sync_user_task_start_events(filters)
        UserTaskEventsSynchronizer.sync_user_task_complete_events(filters)
        UserTaskEventsSynchronizer.sync_user_task_cancel_events(filters)
        print("User task events synchronization completed.")
    except Exception as e:
        print(e)

@trace_span("handler: sync_step_events")
def sync_step_events_(filters: DataSyncSearchFilter):
    try:
        print("Starting step events synchronization...")
        StepEventsSynchronizer.sync_step_create_events(filters),
        print("Step events synchronization completed.")
    except Exception as e:
        print(e)

@trace_span("handler: sync_sleep_events")
def sync_sleep_events_(filters: DataSyncSearchFilter):
    try:
        print("Starting sleep events synchronization...")
        SleepEventsSynchronizer.sync_sleep_create_events(filters),
        print("Step events synchronization completed.")
    except Exception as e:
        print(e)

@trace_span("handler: sync_nutrition_events")
def sync_nutrition_events_(filters: DataSyncSearchFilter):
    try:
        print("Starting nutrition events synchronization...")
        NutritionEventsSynchronizer.sync_nutrition_start_events(filters),
        NutritionEventsSynchronizer.sync_nutrition_update_events(filters),
        NutritionEventsSynchronizer.sync_nutrition_complete_events(filters),
        NutritionEventsSynchronizer.sync_nutrition_cancel_events(filters)
        NutritionEventsSynchronizer.sync_water_intake_create_events(filters)
        NutritionEventsSynchronizer.sync_water_intake_update_events(filters)
        NutritionEventsSynchronizer.sync_water_intake_delete_events(filters)
        print("Nutrition events synchronization completed.")
    except Exception as e:
        print(e)

@trace_span("handler: sync_stand_events")
def sync_stand_events_(filters: DataSyncSearchFilter):
    try:
        print("Starting stand events synchronization...")
        StandEventsSynchronizer.sync_stand_create_events(filters),
        print("Stand events synchronization completed.")
    except Exception as e:
        print(e)

@trace_span("handler: sync_mood_events")
def sync_mood_events_(filters: DataSyncSearchFilter):
    try:
        print("Starting mood events synchronization...")
        MoodEventsSynchronizer.sync_mood_create_events(filters),
        print("Mood events synchronization completed.")
    except Exception as e:
        print(e)

@trace_span("handler: sync_meditation_events")
def sync_meditation_events_(filters: DataSyncSearchFilter):
    try:
        print("Starting meditation events synchronization...")
        MeditationEventsSynchronizer.sync_meditation_start_events(filters),
        MeditationEventsSynchronizer.sync_meditation_complete_events(filters),
        print("Meditation events synchronization completed.")
    except Exception as e:
        print(e)

@trace_span("handler: sync_goal_events")
def sync_goal_events_(filters: DataSyncSearchFilter):
    try:
        print("Starting goal events synchronization...")
        GoalEventsSynchronizer.sync_goal_create_events(filters),
        GoalEventsSynchronizer.sync_goal_start_events(filters),
        GoalEventsSynchronizer.sync_goal_update_events(filters),
        GoalEventsSynchronizer.sync_goal_complete_events(filters),
        GoalEventsSynchronizer.sync_goal_cancel_events(filters),
        print("Goal events synchronization completed.")
    except Exception as e:
        print(e)

@trace_span("handler: sync_exercise_events")
def sync_exercise_events_(filters: DataSyncSearchFilter):
    try:
        print("Starting exercise events synchronization...")
        ExerciseEventsSynchronizer.sync_exercise_start_events(filters),
        ExerciseEventsSynchronizer.sync_exercise_update_events(filters),
        ExerciseEventsSynchronizer.sync_exercise_complete_events(filters),
        ExerciseEventsSynchronizer.sync_exercise_cancel_events(filters),
        print("Exercise events synchronization completed.")
    except Exception as e:
        print(e)
