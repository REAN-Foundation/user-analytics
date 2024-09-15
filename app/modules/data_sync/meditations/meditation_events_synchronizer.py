from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class MeditationEventsSynchronizer:

    #region Add Symptom events

    @staticmethod
    def get_reancare_meditation_start_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND meditation.StartTime between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                meditation.id,
                meditation.EhrId,
                meditation.PatientUserId as UserId,
                meditation.Meditation,
                meditation.Description,
                meditation.Category,
                meditation.DurationInMins,               
                meditation.StartTime,
                meditation.EndTime,
                meditation.CreatedAt,
                meditation.UpdatedAt,
                meditation.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from exercise_meditations as meditation
            JOIN users as user ON meditation.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Meditation Create Events:", error)
            return None

    @staticmethod
    def add_analytics_meditation_start_event(meditation):
        try:
            event_name = EventType.MeditationStart.value
            event_category = EventCategory.Meditation.value
            event_subject = EventSubject.Meditation.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': meditation['EhrId'],
                'PatientUserId': meditation['UserId'],
                'Meditation': meditation['Meditation'],
                'Description': meditation['Description'],
                'Category': meditation['Category'],
                'DurationInMins': meditation['DurationInMins'],
                'StartTime': meditation['StartTime'],
                'EndTime': meditation['EndTime'],
             }
            meditation = {
                'UserId': meditation['UserId'],
                'TenantId': meditation['TenantId'],
                'SessionId': None,
                'ResourceId': meditation['id'],
                'ResourceType': "meditation",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User started a meditation.",
                'Attributes': str(attributes),
                'Timestamp': meditation['StartTime'],
                'UserRegistrationDate': meditation['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(meditation)
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
    def sync_meditation_start_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            meditations = MeditationEventsSynchronizer.get_reancare_meditation_start_events(filters)
            if meditations:
                for meditation in meditations:
                    existing_event = DataSynchronizer.get_existing_event(
                        meditation['UserId'], meditation['id'], EventType.MeditationStart)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = MeditationEventsSynchronizer.add_analytics_meditation_start_event(meditation)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(meditation)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Meditation Start Events found.")
        except Exception as error:
            print(f"Error syncing User Meditation Start Events: {error}")

    #endregion

    @staticmethod
    def get_reancare_meditation_complete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND meditation.EndTime between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                meditation.id,
                meditation.EhrId,
                meditation.PatientUserId as UserId,
                meditation.Meditation,
                meditation.Description,
                meditation.Category,
                meditation.DurationInMins,               
                meditation.StartTime,
                meditation.EndTime,
                meditation.CreatedAt,
                meditation.UpdatedAt,
                meditation.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from exercise_meditations as meditation
            JOIN users as user ON meditation.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                meditation.EndTime IS NOT null
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Meditation Complete Events:", error)
            return None

    @staticmethod
    def add_analytics_meditation_complete_event(meditation):
        try:
            event_name = EventType.MeditationComplete.value
            event_category = EventCategory.Meditation.value
            event_subject = EventSubject.Meditation.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': meditation['EhrId'],
                'PatientUserId': meditation['UserId'],
                'Meditation': meditation['Meditation'],
                'Description': meditation['Description'],
                'Category': meditation['Category'],
                'DurationInMins': meditation['DurationInMins'],
                'StartTime': meditation['StartTime'],
                'EndTime': meditation['EndTime'],
             }
            meditation = {
                'UserId': meditation['UserId'],
                'TenantId': meditation['TenantId'],
                'SessionId': None,
                'ResourceId': meditation['id'],
                'ResourceType': "meditation",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User started a meditation.",
                'Attributes': str(attributes),
                'Timestamp': meditation['EndTime'],
                'UserRegistrationDate': meditation['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(meditation)
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
    def sync_meditation_complete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            meditations = MeditationEventsSynchronizer.get_reancare_meditation_complete_events(filters)
            if meditations:
                for meditation in meditations:
                    existing_event = DataSynchronizer.get_existing_event(
                        meditation['UserId'], meditation['id'], EventType.MeditationComplete)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = MeditationEventsSynchronizer.add_analytics_meditation_complete_event(meditation)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(meditation)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Meditation Complete Events found.")
        except Exception as error:
            print(f"Error syncing User Meditation Complete Events: {error}")

    #endregion


    
