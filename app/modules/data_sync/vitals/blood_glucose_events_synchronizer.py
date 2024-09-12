from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class BloodGlucoseEventsSynchronizer:

    #region Create Blood Glucose events

    @staticmethod
    def get_reancare_blood_glucose_create_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND bloodGlucose.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                bloodGlucose.id,
                bloodGlucose.PatientUserId as UserId,
                bloodGlucose.EhrId,
                bloodGlucose.Provider,
                bloodGlucose.TerraSummaryId,
                bloodGlucose.BloodGlucose,
                bloodGlucose.A1CLevel,
                bloodGlucose.Unit,
                bloodGlucose.RecordDate,
                bloodGlucose.RecordedByUserId,
                bloodGlucose.CreatedAt,
                bloodGlucose.UpdatedAt,
                bloodGlucose.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from biometrics_blood_glucose as bloodGlucose
            JOIN users as user ON bloodGlucose.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Blood Glucose Create Events:", error)
            return None

    @staticmethod
    def add_analytics_blood_glucose_create_event(blood_glucose):
        try:
            event_name = EventType.VitalAddBloodSugar.value
            event_category = EventCategory.Vitals.value
            event_subject = EventSubject.Vital.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': blood_glucose['EhrId'],
                'Provider': blood_glucose['Provider'],
                'TerraSummaryId': blood_glucose['TerraSummaryId'],
                'BloodGlucose': blood_glucose['BloodGlucose'],
                'A1CLevel': blood_glucose['A1CLevel'],
                'Unit': blood_glucose['Unit'],
                'RecordDate': blood_glucose['RecordDate'],
                'RecordedByUserId': blood_glucose['RecordedByUserId'],
            }
            blood_glucose = {
                'UserId': blood_glucose['UserId'],
                'TenantId': blood_glucose['TenantId'],
                'SessionId': None,
                'ResourceId': blood_glucose['id'],
                'ResourceType': "Biometric",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User added a blood glucose.",
                'Attributes': str(attributes),
                'Timestamp': blood_glucose['CreatedAt'],
                'UserRegistrationDate': blood_glucose['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(blood_glucose)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_blood_glucose_create_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            blood_glucose_records = BloodGlucoseEventsSynchronizer.get_reancare_blood_glucose_create_events(filters)
            if blood_glucose_records:
                for blood_glucose in blood_glucose_records:
                    existing_event = DataSynchronizer.get_existing_event(
                        blood_glucose['UserId'], blood_glucose['id'], EventType.VitalAddBloodSugar)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = BloodGlucoseEventsSynchronizer.add_analytics_blood_glucose_create_event(blood_glucose)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(blood_glucose)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Blood Glucose Create Events found.")
        except Exception as error:
            print(f"Error syncing User Blood Glucose Create Events: {error}")

    #endregion

    #region Delete Blood Glucose events

    @staticmethod
    def get_reancare_blood_glucose_delete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND bloodGlucose.DeletedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
             SELECT
                bloodGlucose.id,
                bloodGlucose.PatientUserId as UserId,
                bloodGlucose.EhrId,
                bloodGlucose.Provider,
                bloodGlucose.TerraSummaryId,
                bloodGlucose.BloodGlucose,
                bloodGlucose.A1CLevel,
                bloodGlucose.Unit,
                bloodGlucose.RecordDate,
                bloodGlucose.RecordedByUserId,
                bloodGlucose.CreatedAt,
                bloodGlucose.UpdatedAt,
                bloodGlucose.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from biometrics_blood_glucose as bloodGlucose
            JOIN users as user ON bloodGlucose.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                bloodGlucose.DeletedAt IS NOT NULL
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Blood Glucose Delete Events:", error)
            return None

    @staticmethod
    def add_analytics_blood_glucose_delete_event(blood_glucose):
        try:
            event_name = EventType.VitalDeleteOxygenSaturation.value
            event_category = EventCategory.Vitals.value
            event_subject = EventSubject.Vital.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': blood_glucose['EhrId'],
                'Provider': blood_glucose['Provider'],
                'TerraSummaryId': blood_glucose['TerraSummaryId'],
                'BloodGlucose': blood_glucose['BloodGlucose'],
                'A1CLevel': blood_glucose['A1CLevel'],
                'Unit': blood_glucose['Unit'],
                'RecordDate': blood_glucose['RecordDate'],
                'RecordedByUserId': blood_glucose['RecordedByUserId'],
            }
            blood_glucose = {
                'UserId': blood_glucose['UserId'],
                'TenantId': blood_glucose['TenantId'],
                'SessionId': None,
                'ResourceId': blood_glucose['id'],
                'ResourceType': "Biometric",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User deleted a blood glucose.",
                'Attributes': str(attributes),
                'Timestamp': blood_glucose['DeletedAt'],
                'UserRegistrationDate': blood_glucose['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(blood_glucose)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_blood_glucose_delete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            blood_glucose_records = BloodGlucoseEventsSynchronizer.get_reancare_blood_glucose_delete_events(filters)
            if blood_glucose_records:
                for blood_glucose in blood_glucose_records:
                    existing_event = DataSynchronizer.get_existing_event(
                        blood_glucose['UserId'], blood_glucose['id'], EventType.VitalDeleteBloodSugar)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = BloodGlucoseEventsSynchronizer.add_analytics_blood_glucose_delete_event(blood_glucose)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(blood_glucose)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Blood Glucose Delete Events found.")
        except Exception as error:
            print(f"Error syncing Blood Glucose Delete Events: {error}")

    #endregion

    