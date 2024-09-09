from app.domain_types.enums.event_types import EventType
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class CholesterolEventsSynchronizer:

    #region Create Blood Cholesterol events

    @staticmethod
    def get_reancare_cholesterol_create_events():
        try:
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                cholesterol.id,
                cholesterol.PatientUserId as UserId,
                cholesterol.EhrId,
                cholesterol.TotalCholesterol,
                cholesterol.HDL,
                cholesterol.LDL,
                cholesterol.TriglycerideLevel,
                cholesterol.Ratio,
                cholesterol.A1CLevel,
                cholesterol.Unit,
                cholesterol.RecordDate,
                cholesterol.RecordedByUserId,
                cholesterol.CreatedAt,
                cholesterol.UpdatedAt,
                cholesterol.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from biometrics_blood_cholesterol as cholesterol
            JOIN users as user ON cholesterol.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Blood Cholesterol Create Events:", error)
            return None

    @staticmethod
    def add_analytics_cholesterol_create_event(cholesterol):
        try:
            event_name = EventType.VitalAddBloodSugar.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': cholesterol['EhrId'],
                'TotalCholesterol': cholesterol['TotalCholesterol'],
                'HDL': cholesterol['HDL'],
                'LDL': cholesterol['LDL'],
                'TriglycerideLevel': cholesterol['TriglycerideLevel'],
                'Ratio': cholesterol['Ratio'],
                'A1CLevel': cholesterol['A1CLevel'],
                'Unit': cholesterol['Unit'],
                'RecordDate': cholesterol['RecordDate'],
                'RecordedByUserId': cholesterol['RecordedByUserId'],
            }
            cholesterol = {
                'UserId': cholesterol['UserId'],
                'TenantId': cholesterol['TenantId'],
                'SessionId': None,
                'ResourceId': cholesterol['id'],
                'ResourceType': "Biometric",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventCategory': "Blood-Cholesterol",
                'ActionType': "User-Action",
                'ActionStatement': "User added a blood cholesterol.",
                'Attributes': str(attributes),
                'Timestamp': cholesterol['CreatedAt'],
                'UserRegistrationDate': cholesterol['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(cholesterol)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_cholesterol_create_events():
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            cholesterol_records = CholesterolEventsSynchronizer.get_reancare_cholesterol_create_events()
            if cholesterol_records:
                for cholesterol in cholesterol_records:
                    existing_event = DataSynchronizer.get_existing_event(
                        cholesterol['UserId'], cholesterol['id'], EventType.VitalAddCholesterol)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = CholesterolEventsSynchronizer.add_analytics_cholesterol_create_event(cholesterol)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(cholesterol)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Blood Cholesterol Create Events found.")
        except Exception as error:
            print(f"Error syncing User Blood Cholesterol Create Events: {error}")

    #endregion

    #region Delete Blood Cholesterol events

    @staticmethod
    def get_reancare_cholesterol_delete_events():
        try:
            rean_db_connector = get_reancare_db_connector()
            query = f"""
             SELECT
                cholesterol.id,
                cholesterol.PatientUserId as UserId,
                cholesterol.EhrId,
                cholesterol.TotalCholesterol,
                cholesterol.HDL,
                cholesterol.LDL,
                cholesterol.TriglycerideLevel,
                cholesterol.Ratio,
                cholesterol.A1CLevel,
                cholesterol.Unit,
                cholesterol.RecordDate,
                cholesterol.RecordedByUserId,
                cholesterol.CreatedAt,
                cholesterol.UpdatedAt,
                cholesterol.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from biometrics_blood_cholesterol as cholesterol
            JOIN users as user ON cholesterol.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                cholesterol.DeletedAt IS NOT NULL
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Blood Cholesterol Delete Events:", error)
            return None

    @staticmethod
    def add_analytics_cholesterol_delete_event(cholesterol):
        try:
            event_name = EventType.VitalDeleteCholesterol.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': cholesterol['EhrId'],
                'TotalCholesterol': cholesterol['TotalCholesterol'],
                'HDL': cholesterol['HDL'],
                'LDL': cholesterol['LDL'],
                'TriglycerideLevel': cholesterol['TriglycerideLevel'],
                'Ratio': cholesterol['Ratio'],
                'A1CLevel': cholesterol['A1CLevel'],
                'Unit': cholesterol['Unit'],
                'RecordDate': cholesterol['RecordDate'],
                'RecordedByUserId': cholesterol['RecordedByUserId'],
            }
            cholesterol = {
                'UserId': cholesterol['UserId'],
                'TenantId': cholesterol['TenantId'],
                'SessionId': None,
                'ResourceId': cholesterol['id'],
                'ResourceType': "Biometric",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventCategory': "Blood-Cholesterol",
                'ActionType': "User-Action",
                'ActionStatement': "User deleted a blood cholesterol.",
                'Attributes': str(attributes),
                'Timestamp': cholesterol['DeletedAt'],
                'UserRegistrationDate': cholesterol['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(cholesterol)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_cholesterol_delete_events():
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            cholesterol_records = CholesterolEventsSynchronizer.get_reancare_cholesterol_delete_events()
            if cholesterol_records:
                for cholesterol in cholesterol_records:
                    existing_event = DataSynchronizer.get_existing_event(
                        cholesterol['UserId'], cholesterol['id'], EventType.VitalDeleteCholesterol)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = CholesterolEventsSynchronizer.add_analytics_cholesterol_delete_event(cholesterol)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(cholesterol)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Blood Cholesterol Delete Events found.")
        except Exception as error:
            print(f"Error syncing Blood Cholesterol Delete Events: {error}")

    #endregion

    