from app.domain_types.enums.event_types import EventType
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class PulseEventsSynchronizer:

    #region Create Pulse events

    @staticmethod
    def get_reancare_pulse_create_events():
        try:
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                pulse.id,
                pulse.PatientUserId as UserId,
                pulse.EhrId,
                pulse.Provider,
                pulse.TerraSummaryId,
                pulse.Pulse,
                pulse.Unit,
                pulse.RecordDate,
                pulse.RecordedByUserId,
                pulse.CreatedAt,
                pulse.UpdatedAt,
                pulse.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from biometrics_pulse as pulse
            JOIN users as user ON pulse.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Biometrics-Pulse Create Events:", error)
            return None

    @staticmethod
    def add_analytics_pulse_create_event(pulse):
        try:
            event_name = EventType.VitalAddPulse.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': pulse['EhrId'],
                'Provider': pulse['Provider'],
                'TerraSummaryId': pulse['TerraSummaryId'],
                'Pulse': pulse['Pulse'],
                'Unit': pulse['Unit'],
                'RecordDate': pulse['RecordDate'],
                'RecordedByUserId': pulse['RecordedByUserId'],
            }
            pulse = {
                'UserId': pulse['UserId'],
                'TenantId': pulse['TenantId'],
                'SessionId': None,
                'ResourceId': pulse['id'],
                'ResourceType': "Biometric",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventCategory': "Pulse",
                'ActionType': "User-Action",
                'ActionStatement': "User added a biometric pulse.",
                'Attributes': str(attributes),
                'Timestamp': pulse['CreatedAt'],
                'UserRegistrationDate': pulse['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(pulse)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_pulse_create_events():
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            pulses = PulseEventsSynchronizer.get_reancare_pulse_create_events()
            if pulses:
                for pulse in pulses:
                    existing_event = DataSynchronizer.get_existing_event(
                        pulse['UserId'], pulse['id'], EventType.VitalAddPulse)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = PulseEventsSynchronizer.add_analytics_pulse_create_event(pulse)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(pulse)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Pulse Create Events found.")
        except Exception as error:
            print(f"Error syncing User Pulse Create Events: {error}")

    #endregion

    #region Delete Pulse events

    @staticmethod
    def get_reancare_pulse_delete_events():
        try:
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                pulse.id,
                pulse.PatientUserId as UserId,
                pulse.EhrId,
                pulse.Provider,
                pulse.TerraSummaryId,
                pulse.Pulse,
                pulse.Unit,
                pulse.RecordDate,
                pulse.RecordedByUserId,
                pulse.CreatedAt,
                pulse.UpdatedAt,
                pulse.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from biometrics_pulse as pulse
            JOIN users as user ON pulse.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                pulse.DeletedAt IS NOT NULL
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Pulse Delete Events:", error)
            return None

    @staticmethod
    def add_analytics_pulse_delete_event(pulse):
        try:
            event_name = EventType.VitalDeletePulse.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': pulse['EhrId'],
                'Provider': pulse['Provider'],
                'TerraSummaryId': pulse['TerraSummaryId'],
                'Pulse': pulse['Pulse'],
                'Unit': pulse['Unit'],
                'RecordDate': pulse['RecordDate'],
                'RecordedByUserId': pulse['RecordedByUserId'],
            }
            pulse = {
                'UserId': pulse['UserId'],
                'TenantId': pulse['TenantId'],
                'SessionId': None,
                'ResourceId': pulse['id'],
                'ResourceType': "Biometric",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventCategory': "Pulse",
                'ActionType': "User-Action",
                'ActionStatement': "User deleted a biometric pulse.",
                'Attributes': str(attributes),
                'Timestamp': pulse['DeletedAt'],
                'UserRegistrationDate': pulse['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(pulse)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_pulse_delete_events():
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            deleted_pulses = PulseEventsSynchronizer.get_reancare_pulse_delete_events()
            if deleted_pulses:
                for pulse in deleted_pulses:
                    existing_event = DataSynchronizer.get_existing_event(
                        pulse['UserId'], pulse['id'], EventType.VitalDeletePulse)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = PulseEventsSynchronizer.add_analytics_pulse_delete_event(pulse)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(pulse)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Pulse Delete Events found.")
        except Exception as error:
            print(f"Error syncing User Pulse Delete Events: {error}")

    #endregion

    