from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class BodyWeightEventsSynchronizer:

    #region Create Body Weight events

    @staticmethod
    def get_reancare_body_weight_create_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND bodyWeight.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                bodyWeight.id,
                bodyWeight.PatientUserId as UserId,
                bodyWeight.EhrId,
                bodyWeight.BodyWeight,
                bodyWeight.Unit,
                bodyWeight.RecordDate,
                bodyWeight.RecordedByUserId,
                bodyWeight.CreatedAt,
                bodyWeight.UpdatedAt,
                bodyWeight.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from biometrics_body_weight as bodyWeight
            JOIN users as user ON bodyWeight.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Biometrics-Body Weight Create Events:", error)
            return None

    @staticmethod
    def add_analytics_body_weight_create_event(body_weight):
        try:
            event_name = EventType.VitalsAdd.value
            event_category = EventCategory.Vitals.value
            event_subject = EventSubject.VitalsBodyWeight.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': body_weight['EhrId'],
                'BodyWeight': body_weight['BodyWeight'],
                'Unit': body_weight['Unit'],
                'RecordDate': body_weight['RecordDate'],
                'RecordedByUserId': body_weight['RecordedByUserId'],
            }
            body_weight = {
                'UserId': body_weight['UserId'],
                'TenantId': body_weight['TenantId'],
                'SessionId': None,
                'ResourceId': body_weight['id'],
                'ResourceType': "biometric",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User added a biometric body weight.",
                'Attributes': str(attributes),
                'Timestamp': body_weight['CreatedAt'],
                'UserRegistrationDate': body_weight['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(body_weight)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_body_weight_create_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            body_weights = BodyWeightEventsSynchronizer.get_reancare_body_weight_create_events(filters)
            if body_weights:
                for body_weight in body_weights:
                    existing_event = DataSynchronizer.get_existing_event(
                        body_weight['UserId'], body_weight['id'], EventType.VitalsAdd)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = BodyWeightEventsSynchronizer.add_analytics_body_weight_create_event(body_weight)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(body_weight)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Body Weight Create Events found.")
        except Exception as error:
            print(f"Error syncing User Body Weight Create Events: {error}")

    #endregion

    #region Delete Body Weight events

    @staticmethod
    def get_reancare_body_weight_delete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND bodyWeight.DeletedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                bodyWeight.id,
                bodyWeight.PatientUserId as UserId,
                bodyWeight.EhrId,
                bodyWeight.BodyWeight,
                bodyWeight.Unit,
                bodyWeight.RecordDate,
                bodyWeight.RecordedByUserId,
                bodyWeight.CreatedAt,
                bodyWeight.UpdatedAt,
                bodyWeight.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from biometrics_body_weight as bodyWeight
            JOIN users as user ON bodyWeight.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                bodyWeight.DeletedAt IS NOT NULL
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Body Weight Delete Events:", error)
            return None

    @staticmethod
    def add_analytics_body_weight_delete_event(body_weight):
        try:
            event_name = EventType.VitalsDelete.value
            event_category = EventCategory.Vitals.value
            event_subject = EventSubject.VitalsBodyWeight.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': body_weight['EhrId'],
                'BodyWeight': body_weight['BodyWeight'],
                'Unit': body_weight['Unit'],
                'RecordDate': body_weight['RecordDate'],
                'RecordedByUserId': body_weight['RecordedByUserId'],
            }
            body_weight = {
                'UserId': body_weight['UserId'],
                'TenantId': body_weight['TenantId'],
                'SessionId': None,
                'ResourceId': body_weight['id'],
                'ResourceType': "biometric",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User deleted a biometric body weight.",
                'Attributes': str(attributes),
                'Timestamp': body_weight['DeletedAt'],
                'UserRegistrationDate': body_weight['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(body_weight)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_body_weight_delete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            deleted_body_weights = BodyWeightEventsSynchronizer.get_reancare_body_weight_delete_events(filters)
            if deleted_body_weights:
                for body_weight in deleted_body_weights:
                    existing_event = DataSynchronizer.get_existing_event(
                        body_weight['UserId'], body_weight['id'], EventType.VitalsAdd)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = BodyWeightEventsSynchronizer.add_analytics_body_weight_delete_event(body_weight)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(body_weight)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Body Weight Delete Events found.")
        except Exception as error:
            print(f"Error syncing User Body Weight Delete Events: {error}")

    #endregion

    