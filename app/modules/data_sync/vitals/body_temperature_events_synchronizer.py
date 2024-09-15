from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class BodyTemperatureEventsSynchronizer:

    #region Create Body Temperature events

    @staticmethod
    def get_reancare_body_temperature_create_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND bodyTemperature.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                bodyTemperature.id,
                bodyTemperature.PatientUserId as UserId,
                bodyTemperature.EhrId,
                bodyTemperature.Provider,
                bodyTemperature.TerraSummaryId,
                bodyTemperature.BodyTemperature,
                bodyTemperature.Unit,
                bodyTemperature.RecordDate,
                bodyTemperature.RecordedByUserId,
                bodyTemperature.CreatedAt,
                bodyTemperature.UpdatedAt,
                bodyTemperature.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from biometrics_body_temperature as bodyTemperature
            JOIN users as user ON bodyTemperature.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Biometrics-Body Temperature Create Events:", error)
            return None

    @staticmethod
    def add_analytics_body_temperature_create_event(body_temperature):
        try:
            event_name = EventType.VitalsAdd.value
            event_category = EventCategory.Vitals.value
            event_subject = EventSubject.VitalsBodyTemperature.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': body_temperature['EhrId'],
                'Provider': body_temperature['Provider'],
                'TerraSummaryId': body_temperature['TerraSummaryId'],
                'BodyTemperature': body_temperature['BodyTemperature'],
                'Unit': body_temperature['Unit'],
                'RecordDate': body_temperature['RecordDate'],
                'RecordedByUserId': body_temperature['RecordedByUserId'],
            }
            body_temperature = {
                'UserId': body_temperature['UserId'],
                'TenantId': body_temperature['TenantId'],
                'SessionId': None,
                'ResourceId': body_temperature['id'],
                'ResourceType': "biometric",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User added a biometric body temperature.",
                'Attributes': str(attributes),
                'Timestamp': body_temperature['CreatedAt'],
                'UserRegistrationDate': body_temperature['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(body_temperature)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_body_temperature_create_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            body_temperatures = BodyTemperatureEventsSynchronizer.get_reancare_body_temperature_create_events(filters)
            if body_temperatures:
                for body_temperature in body_temperatures:
                    existing_event = DataSynchronizer.get_existing_event(
                        body_temperature['UserId'], body_temperature['id'], EventType.VitalsAdd)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = BodyTemperatureEventsSynchronizer.add_analytics_body_temperature_create_event(body_temperature)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(body_temperature)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Body Temperature Create Events found.")
        except Exception as error:
            print(f"Error syncing User Body Temperature Create Events: {error}")

    #endregion

    #region Delete Body Temperature events

    @staticmethod
    def get_reancare_body_temperature_delete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND bodyTemperature.DeletedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                bodyTemperature.id,
                bodyTemperature.PatientUserId as UserId,
                bodyTemperature.EhrId,
                bodyTemperature.Provider,
                bodyTemperature.TerraSummaryId,
                bodyTemperature.BodyTemperature,
                bodyTemperature.Unit,
                bodyTemperature.RecordDate,
                bodyTemperature.RecordedByUserId,
                bodyTemperature.CreatedAt,
                bodyTemperature.UpdatedAt,
                bodyTemperature.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from biometrics_body_temperature as bodyTemperature
            JOIN users as user ON bodyTemperature.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                bodyTemperature.DeletedAt IS NOT NULL
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Body Temperature Delete Events:", error)
            return None

    @staticmethod
    def add_analytics_body_temperature_delete_event(body_temperature):
        try:
            event_name = EventType.VitalsDelete.value
            event_category = EventCategory.Vitals.value
            event_subject = EventSubject.VitalsBodyTemperature.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': body_temperature['EhrId'],
                'Provider': body_temperature['Provider'],
                'TerraSummaryId': body_temperature['TerraSummaryId'],
                'BodyTemperature': body_temperature['BodyTemperature'],
                'Unit': body_temperature['Unit'],
                'RecordDate': body_temperature['RecordDate'],
                'RecordedByUserId': body_temperature['RecordedByUserId'],
            }
            body_temperature = {
                'UserId': body_temperature['UserId'],
                'TenantId': body_temperature['TenantId'],
                'SessionId': None,
                'ResourceId': body_temperature['id'],
                'ResourceType': "biometric",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User deleted a biometric body temperature.",
                'Attributes': str(attributes),
                'Timestamp': body_temperature['DeletedAt'],
                'UserRegistrationDate': body_temperature['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(body_temperature)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_body_temperature_delete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            deleted_body_temperatures = BodyTemperatureEventsSynchronizer.get_reancare_body_temperature_delete_events(filters)
            if deleted_body_temperatures:
                for body_temperature in deleted_body_temperatures:
                    existing_event = DataSynchronizer.get_existing_event(
                        body_temperature['UserId'], body_temperature['id'], EventType.VitalsDelete)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = BodyTemperatureEventsSynchronizer.add_analytics_body_temperature_delete_event(body_temperature)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(body_temperature)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Body Temperature Delete Events found.")
        except Exception as error:
            print(f"Error syncing User Body Temperature Delete Events: {error}")

    #endregion

    