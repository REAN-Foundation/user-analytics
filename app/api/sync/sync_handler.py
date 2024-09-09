from typing import Optional
from app.common.validators import validate_uuid4
from app.modules.data_sync.blood_glucose_events_synchronizer import BloodGlucoseEventsSynchronizer
from app.modules.data_sync.cholesterol_events_synchronizer import CholesterolEventsSynchronizer
from app.modules.data_sync.oxygen_saturation_events_synchronizer import OxygenSaturationEventsSynchronizer
from app.modules.data_sync.blood_pressure_events_synchronizer import BloodPressureEventsSynchronizer
from app.modules.data_sync.body_height_events_synchronizer import BodyHeightEventsSynchronizer
from app.modules.data_sync.body_temperature_events_synchronizer import BodyTemperatureEventsSynchronizer
from app.modules.data_sync.body_weight_events_synchronizer import BodyWeightEventsSynchronizer
from app.modules.data_sync.data_synchronizer import DataSynchronizer
from app.modules.data_sync.lab_record_events_synchonizer import LabRecordEventsSynchronizer
from app.modules.data_sync.login_events_synchonizer import LoginEventsSynchronizer
from app.modules.data_sync.medication_events_synchronizer import MedicationEventsSynchronizer
from app.modules.data_sync.pulse_events_synchronizer import PulseEventsSynchronizer
from app.modules.data_sync.symptom_events_synchronizer import SymptomEventsSynchronizer
from app.telemetry.tracing import trace_span

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

@trace_span("handler: sync_medication_create_events")
def sync_medication_create_events_():
    try:
        MedicationEventsSynchronizer.sync_medication_create_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_medication_delete_events")
def sync_medication_delete_events_():
    try:
        MedicationEventsSynchronizer.sync_medication_delete_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_medication_schedule_taken_events")
def sync_medication_schedule_taken_events_():
    try:
        MedicationEventsSynchronizer.sync_medication_schedule_taken_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_medication_schedule_missed_events")
def sync_medication_schedule_missed_events_():
    try:
        MedicationEventsSynchronizer.sync_medication_schedule_missed_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_symptom_create_events")
def sync_symptom_create_events_():
    try:
        SymptomEventsSynchronizer.sync_symptom_create_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_symptom_update_events")
def sync_symptom_update_events_():
    try:
        SymptomEventsSynchronizer.sync_symptom_update_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_symptom_delete_events")
def sync_symptom_delete_events_():
    try:
        SymptomEventsSynchronizer.sync_symptom_delete_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_lab_record_create_events")
def sync_lab_record_create_events_():
    try:
        LabRecordEventsSynchronizer.sync_lab_record_create_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_lab_record_delete_events")
def sync_lab_record_delete_events_():
    try:
        LabRecordEventsSynchronizer.sync_lab_record_delete_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_pulse_create_events")
def sync_pulse_create_events_():
    try:
        PulseEventsSynchronizer.sync_pulse_create_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_pulse_delete_events")
def sync_pulse_delete_events_():
    try:
        PulseEventsSynchronizer.sync_pulse_delete_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_body_weight_create_events")
def sync_body_weight_create_events_():
    try:
        BodyWeightEventsSynchronizer.sync_body_weight_create_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_body_weight_delete_events")
def sync_body_weight_delete_events_():
    try:
        BodyWeightEventsSynchronizer.sync_body_weight_delete_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_body_temperature_create_events")
def sync_body_temperature_create_events_():
    try:
        BodyTemperatureEventsSynchronizer.sync_body_temperature_create_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_body_temperature_delete_events")
def sync_body_temperature_delete_events_():
    try:
        BodyTemperatureEventsSynchronizer.sync_body_temperature_delete_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_body_height_create_events")
def sync_body_height_create_events_():
    try:
        BodyHeightEventsSynchronizer.sync_body_height_create_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_body_height_delete_events")
def sync_body_height_delete_events_():
    try:
        BodyHeightEventsSynchronizer.sync_body_height_delete_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_blood_pressure_create_events")
def sync_blood_pressure_create_events_():
    try:
        BloodPressureEventsSynchronizer.sync_blood_pressure_create_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_blood_pressure_delete_events")
def sync_blood_pressure_delete_events_():
    try:
        BloodPressureEventsSynchronizer.sync_blood_pressure_delete_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_oxygen_saturation_create_events")
def sync_oxygen_saturation_create_events_():
    try:
        OxygenSaturationEventsSynchronizer.sync_oxygen_saturation_create_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_oxygen_saturation_delete_events")
def sync_oxygen_saturation_delete_events_():
    try:
        OxygenSaturationEventsSynchronizer.sync_oxygen_saturation_delete_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_blood_glucose_create_events")
def sync_blood_glucose_create_events_():
    try:
        BloodGlucoseEventsSynchronizer.sync_blood_glucose_create_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_blood_glucose_delete_events")
def sync_blood_glucose_delete_events_():
    try:
        BloodGlucoseEventsSynchronizer.sync_blood_glucose_delete_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_cholesterol_create_events")
def sync_cholesterol_create_events_():
    try:
        CholesterolEventsSynchronizer.sync_cholesterol_create_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_cholesterol_delete_events")
def sync_cholesterol_delete_events_():
    try:
        CholesterolEventsSynchronizer.sync_cholesterol_delete_events()
    except Exception as e:
        print(e)

