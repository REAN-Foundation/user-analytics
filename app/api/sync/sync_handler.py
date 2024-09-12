from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.lab_records.lab_record_events_synchonizer import LabRecordEventsSynchronizer
from app.modules.data_sync.symptoms.symptom_events_synchronizer import SymptomEventsSynchronizer
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
