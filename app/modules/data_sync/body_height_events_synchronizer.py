from app.domain_types.enums.event_types import EventType
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class BodyHeightEventsSynchronizer:

    #region Create Body Height events

    @staticmethod
    def get_reancare_body_height_create_events():
        try:
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
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Biometrics-Body Height Create Events:", error)
            return None

    @staticmethod
    def add_analytics_body_height_create_event(body_height):
        try:
            event_name = EventType.VitalAddHeight.value
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
                'ResourceType': "Biometric",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventCategory': "Body-Height",
                'ActionType': "User-Action",
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
    def sync_body_height_create_events():
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            body_heights = BodyHeightEventsSynchronizer.get_reancare_body_height_create_events()
            if body_heights:
                for body_height in body_heights:
                    existing_event = DataSynchronizer.get_existing_event(
                        body_height['UserId'], body_height['id'], EventType.VitalAddHeight)
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
    def get_reancare_body_height_delete_events():
        try:
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
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Body Height Delete Events:", error)
            return None

    @staticmethod
    def add_analytics_body_height_delete_event(body_height):
        try:
            event_name = EventType.VitalDeleteHeight.value
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
                'ResourceType': "Biometric",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventCategory': "Body-Height",
                'ActionType': "User-Action",
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
    def sync_body_height_delete_events():
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            deleted_body_heights = BodyHeightEventsSynchronizer.get_reancare_body_height_delete_events()
            if deleted_body_heights:
                for body_height in deleted_body_heights:
                    existing_event = DataSynchronizer.get_existing_event(
                        body_height['UserId'], body_height['id'], EventType.VitalDeleteHeight)
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

    