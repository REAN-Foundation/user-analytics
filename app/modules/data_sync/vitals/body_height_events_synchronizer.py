from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class BodyHeightEventsSynchronizer:

    #region Create Body Height events

    @staticmethod
    def get_reancare_body_height_create_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND bodyHeight.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                bodyHeight.id,
                bodyHeight.PatientUserId as UserId,
                bodyHeight.EhrId,
                bodyHeight.BodyHeight,
                bodyHeight.Unit,
                bodyHeight.RecordDate,
                bodyHeight.RecordedByUserId,
                bodyHeight.CreatedAt,
                bodyHeight.UpdatedAt,
                bodyHeight.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from biometrics_body_height as bodyHeight
            JOIN users as user ON bodyHeight.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Biometrics-Body Height Create Events:", error)
            return None

    @staticmethod
    def add_analytics_body_height_create_event(body_height):
        try:
            event_name = EventType.VitalsAdd.value
            event_category = EventCategory.Vitals.value
            event_subject = EventSubject.VitalsBodyHeight.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': body_height['EhrId'],
                'BodyWeight': body_height['BodyHeight'],
                'Unit': body_height['Unit'],
                'RecordDate': body_height['RecordDate'],
                'RecordedByUserId': body_height['RecordedByUserId'],
            }
            body_height = {
                'UserId': body_height['UserId'],
                'TenantId': body_height['TenantId'],
                'SessionId': None,
                'ResourceId': body_height['id'],
                'ResourceType': "biometric",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User added a body height.",
                'Attributes': str(attributes),
                'Timestamp': body_height['CreatedAt'],
                'UserRegistrationDate': body_height['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(body_height)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_body_height_create_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            body_heights = BodyHeightEventsSynchronizer.get_reancare_body_height_create_events(filters)
            if body_heights:
                for body_height in body_heights:
                    existing_event = DataSynchronizer.get_existing_event(
                        body_height['UserId'], body_height['id'], EventType.VitalsAdd)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = BodyHeightEventsSynchronizer.add_analytics_body_height_create_event(body_height)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(body_height)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Body Height Create Events found.")
        except Exception as error:
            print(f"Error syncing User Body Height Create Events: {error}")

    #endregion

    #region Delete Body Height events

    @staticmethod
    def get_reancare_body_height_delete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND bodyHeight.DeletedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                bodyHeight.id,
                bodyHeight.PatientUserId as UserId,
                bodyHeight.EhrId,
                bodyHeight.BodyHeight,
                bodyHeight.Unit,
                bodyHeight.RecordDate,
                bodyHeight.RecordedByUserId,
                bodyHeight.CreatedAt,
                bodyHeight.UpdatedAt,
                bodyHeight.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from biometrics_body_height as bodyHeight
            JOIN users as user ON bodyHeight.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                bodyHeight.DeletedAt IS NOT NULL
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Body Height Delete Events:", error)
            return None

    @staticmethod
    def add_analytics_body_height_delete_event(body_height):
        try:
            event_name = EventType.VitalsDelete.value
            event_category = EventCategory.Vitals.value
            event_subject = EventSubject.VitalsBodyHeight.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': body_height['EhrId'],
                'BodyWeight': body_height['BodyWeight'],
                'Unit': body_height['Unit'],
                'RecordDate': body_height['RecordDate'],
                'RecordedByUserId': body_height['RecordedByUserId'],
            }
            body_height = {
                'UserId': body_height['UserId'],
                'TenantId': body_height['TenantId'],
                'SessionId': None,
                'ResourceId': body_height['id'],
                'ResourceType': "biometric",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User deleted a biometric-body weight.",
                'Attributes': str(attributes),
                'Timestamp': body_height['DeletedAt'],
                'UserRegistrationDate': body_height['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(body_height)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_body_height_delete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            deleted_body_heights = BodyHeightEventsSynchronizer.get_reancare_body_height_delete_events(filters)
            if deleted_body_heights:
                for body_height in deleted_body_heights:
                    existing_event = DataSynchronizer.get_existing_event(
                        body_height['UserId'], body_height['id'], EventType.VitalsDelete)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = BodyHeightEventsSynchronizer.add_analytics_body_height_delete_event(body_height)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(body_height)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Body Height Delete Events found.")
        except Exception as error:
            print(f"Error syncing User Body Height Delete Events: {error}")

    #endregion

    