from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class SleepEventsSynchronizer:

    #region Add Symptom events

    @staticmethod
    def get_reancare_sleep_create_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND sleep.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                sleep.id,                
                sleep.PatientUserId as UserId,
                sleep.SleepDuration,
                sleep.SleepMinutes,
                sleep.Unit,
                sleep.RecordDate,
                sleep.CreatedAt,
                sleep.UpdatedAt,
                sleep.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from daily_records_sleep as sleep
            JOIN users as user ON sleep.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            print(query)
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User sleep Create Events:", error)
            return None

    @staticmethod
    def add_analytics_sleep_create_event(sleep):
        try:
            event_name = EventType.SleepRecordAdd.value
            event_category = EventCategory.Sleep.value
            event_subject = EventSubject.Sleep.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'SleepDuration': sleep['SleepDuration'],
                'SleepMinutes': sleep['SleepMinutes'], 
                'Unit': sleep['Unit'],
                'RecordDate': sleep['RecordDate'],               
             }
            sleep = {
                'UserId': sleep['UserId'],
                'TenantId': sleep['TenantId'],
                'SessionId': None,
                'ResourceId': sleep['id'],
                'ResourceType': "sleep",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User added a sleep.",
                'Attributes': str(attributes),
                'Timestamp': sleep['CreatedAt'],
                'UserRegistrationDate': sleep['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(sleep)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                # print(f"Inserted row into the user_medication_create_events table.")
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_sleep_create_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            sleeps = SleepEventsSynchronizer.get_reancare_sleep_create_events(filters)
            if sleeps:
                for sleep in sleeps:
                    existing_event = DataSynchronizer.get_existing_event(
                        sleep['UserId'], sleep['id'], EventType.SleepRecordAdd)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = SleepEventsSynchronizer.add_analytics_sleep_create_event(sleep)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(sleep)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Sleep Create Events found.")
        except Exception as error:
            print(f"Error syncing User Sleep Create Events: {error}")
    
    #endregion
