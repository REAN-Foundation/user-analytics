from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class BloodPressureEventsSynchronizer:

    #region Create Blood Pressure events

    @staticmethod
    def get_reancare_blood_pressure_create_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND bloodPressure.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                bloodPressure.id,
                bloodPressure.PatientUserId as UserId,
                bloodPressure.EhrId,
                bloodPressure.Provider,
                bloodPressure.TerraSummaryId,
                bloodPressure.Systolic,
                bloodPressure.Diastolic,
                bloodPressure.Unit,
                bloodPressure.RecordDate,
                bloodPressure.RecordedByUserId,
                bloodPressure.CreatedAt,
                bloodPressure.UpdatedAt,
                bloodPressure.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from biometrics_blood_pressure as bloodPressure
            JOIN users as user ON bloodPressure.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Blood Pressure Create Events:", error)
            return None

    @staticmethod
    def add_analytics_blood_pressure_create_event(blood_pressure):
        try:
            event_name = EventType.VitalsAdd.value
            event_category = EventCategory.Vitals.value
            event_subject = EventSubject.VitalsBloodPressure.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': blood_pressure['EhrId'],
                'Provider': blood_pressure['Provider'],
                'TerraSummaryId': blood_pressure['TerraSummaryId'],
                'Systolic': blood_pressure['Systolic'],
                'Diastolic': blood_pressure['Diastolic'],
                'Unit': blood_pressure['Unit'],
                'RecordDate': blood_pressure['RecordDate'],
                'RecordedByUserId': blood_pressure['RecordedByUserId'],
            }
            blood_pressure = {
                'UserId': blood_pressure['UserId'],
                'TenantId': blood_pressure['TenantId'],
                'SessionId': None,
                'ResourceId': blood_pressure['id'],
                'ResourceType': "biometric",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User added a blood pressure.",
                'Attributes': str(attributes),
                'Timestamp': blood_pressure['CreatedAt'],
                'UserRegistrationDate': blood_pressure['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(blood_pressure)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_blood_pressure_create_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            blood_pressure_records = BloodPressureEventsSynchronizer.get_reancare_blood_pressure_create_events(filters)
            if blood_pressure_records:
                for blood_pressure in blood_pressure_records:
                    existing_event = DataSynchronizer.get_existing_event(
                        blood_pressure['UserId'], blood_pressure['id'], EventType.VitalsAdd)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = BloodPressureEventsSynchronizer.add_analytics_blood_pressure_create_event(blood_pressure)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(blood_pressure)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Blood Pressure Create Events found.")
        except Exception as error:
            print(f"Error syncing User Blood Pressure Create Events: {error}")

    #endregion

    #region Delete Blood Pressure events

    @staticmethod
    def get_reancare_blood_pressure_delete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND bloodPressure.DeletedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                bloodPressure.id,
                bloodPressure.PatientUserId as UserId,
                bloodPressure.EhrId,
                bloodPressure.Provider,
                bloodPressure.TerraSummaryId,
                bloodPressure.Systolic,
                bloodPressure.Diastolic,
                bloodPressure.Unit,
                bloodPressure.RecordDate,
                bloodPressure.RecordedByUserId,
                bloodPressure.CreatedAt,
                bloodPressure.UpdatedAt,
                bloodPressure.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from biometrics_blood_pressure as bloodPressure
            JOIN users as user ON bloodPressure.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                bloodPressure.DeletedAt IS NOT NULL
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Blood Pressure Delete Events:", error)
            return None

    @staticmethod
    def add_analytics_blood_pressure_delete_event(blood_pressure):
        try:
            event_name = EventType.VitalsDelete.value
            event_category = EventCategory.Vitals.value
            event_subject = EventSubject.VitalsBloodPressure.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
               'EhrId': blood_pressure['EhrId'],
                'Provider': blood_pressure['Provider'],
                'TerraSummaryId': blood_pressure['TerraSummaryId'],
                'Systolic': blood_pressure['Systolic'],
                'Diastolic': blood_pressure['Diastolic'],
                'Unit': blood_pressure['Unit'],
                'RecordDate': blood_pressure['RecordDate'],
                'RecordedByUserId': blood_pressure['RecordedByUserId']
            }
            blood_pressure = {
                 'UserId': blood_pressure['UserId'],
                'TenantId': blood_pressure['TenantId'],
                'SessionId': None,
                'ResourceId': blood_pressure['id'],
                'ResourceType': "biometric",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User deleted a blood pressure.",
                'Attributes': str(attributes),
                'Timestamp': blood_pressure['DeletedAt'],
                'UserRegistrationDate': blood_pressure['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(blood_pressure)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_blood_pressure_delete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            deleted_blood_pressure_records = BloodPressureEventsSynchronizer.get_reancare_blood_pressure_delete_events(filters)
            if deleted_blood_pressure_records:
                for blood_pressure in deleted_blood_pressure_records:
                    existing_event = DataSynchronizer.get_existing_event(
                        blood_pressure['UserId'], blood_pressure['id'], EventType.VitalsDelete)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = BloodPressureEventsSynchronizer.add_analytics_blood_pressure_delete_event(blood_pressure)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(blood_pressure)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Blood Pressure Delete Events found.")
        except Exception as error:
            print(f"Error syncing User Blood Pressure Delete Events: {error}")

    #endregion

    