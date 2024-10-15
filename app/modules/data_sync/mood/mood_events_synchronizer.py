from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class MoodEventsSynchronizer:

    #region Add Mood events

    @staticmethod
    def get_reancare_mood_create_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND mood.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                mood.id,
                mood.EhrId,
                mood.PatientUserId as UserId,
                mood.Feeling,
                mood.Mood,
                mood.EnergyLevels,
                mood.RecordDate,
                mood.CreatedAt,
                mood.UpdatedAt,
                mood.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from daily_assessments as mood
            JOIN users as user ON mood.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Mood Create Events:", error)
            return None

    @staticmethod
    def add_analytics_mood_create_event(mood):
        try:
            event_name = EventType.SymptomAdd.value
            event_category = EventCategory.Symptoms.value
            event_subject = mood['Feeling']
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': mood['EhrId'],
                'PatientUserId': mood['UserId'],
                'Feeling': mood['Feeling'],
                'Mood': mood['Mood'], 
                'EnergyLevels': mood['EnergyLevels'],
                'RecordDate': mood['RecordDate']           
             }
            mood = {
                'UserId': mood['UserId'],
                'TenantId': mood['TenantId'],
                'SessionId': None,
                'ResourceId': mood['id'],
                'ResourceType': "symptom-how-do-you-feel",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User added mood record.",
                'Attributes': str(attributes),
                'Timestamp': mood['CreatedAt'],
                'UserRegistrationDate': mood['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(mood)
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
    def sync_mood_create_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            moods = MoodEventsSynchronizer.get_reancare_mood_create_events(filters)
            if moods:
                for mood in moods:
                    existing_event = DataSynchronizer.get_existing_event(
                        mood['UserId'], mood['id'], EventType.SymptomAdd)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = MoodEventsSynchronizer.add_analytics_mood_create_event(mood)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(mood)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Mood Create Events found.")
        except Exception as error:
            print(f"Error syncing User Mood Create Events: {error}")
    
    #endregion

    #region Update Mood events

    @staticmethod
    def get_reancare_mood_update_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND mood.UpdatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                mood.id,
                mood.EhrId,
                mood.PatientUserId as UserId,
                mood.Feeling,
                mood.Mood,
                mood.EnergyLevels,
                mood.RecordDate,
                mood.CreatedAt,
                mood.UpdatedAt,
                mood.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from daily_assessments as mood
            JOIN users as user ON mood.PatientUserId = user.id
            WHERE
                mood.UpdatedAt <> mood.CreatedAt
                AND
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Mood Update Events:", error)
            return None

    @staticmethod
    def add_analytics_mood_update_event(mood):
        try:
            event_name = EventType.SymptomUpdate.value
            event_category = EventCategory.Symptoms.value
            event_subject = mood['Feeling']
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': mood['EhrId'],
                'PatientUserId': mood['UserId'],
                'Feeling': mood['Feeling'],
                'Mood': mood['Mood'], 
                'EnergyLevels': mood['EnergyLevels'],
                'RecordDate': mood['RecordDate']           
             }
            mood = {
                'UserId': mood['UserId'],
                'TenantId': mood['TenantId'],
                'SessionId': None,
                'ResourceId': mood['id'],
                'ResourceType': "symptom-how-do-you-feel",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User updated mood record.",
                'Attributes': str(attributes),
                'Timestamp': mood['UpdatedAt'],
                'UserRegistrationDate': mood['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(mood)
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
    def sync_mood_update_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            moods = MoodEventsSynchronizer.get_reancare_mood_update_events(filters)
            if moods:
                for mood in moods:
                    existing_event = DataSynchronizer.get_existing_event(
                        mood['UserId'], mood['id'], EventType.SymptomUpdate)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = MoodEventsSynchronizer.add_analytics_mood_update_event(mood)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(mood)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Mood Update Events found.")
        except Exception as error:
            print(f"Error syncing User Mood Update Events: {error}")
    
    #endregion

    #region Delete Mood events

    @staticmethod
    def get_reancare_mood_delete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND mood.DeletedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                mood.id,
                mood.EhrId,
                mood.PatientUserId as UserId,
                mood.Feeling,
                mood.Mood,
                mood.EnergyLevels,
                mood.RecordDate,
                mood.CreatedAt,
                mood.UpdatedAt,
                mood.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from daily_assessments as mood
            JOIN users as user ON mood.PatientUserId = user.id
            WHERE
                mood.DeletedAt IS NOT null
                AND
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Mood Delete Events:", error)
            return None

    @staticmethod
    def add_analytics_mood_delete_event(mood):
        try:
            event_name = EventType.SymptomDelete.value
            event_category = EventCategory.Symptoms.value
            event_subject = mood['Feeling']
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': mood['EhrId'],
                'PatientUserId': mood['UserId'],
                'Feeling': mood['Feeling'],
                'Mood': mood['Mood'], 
                'EnergyLevels': mood['EnergyLevels'],
                'RecordDate': mood['RecordDate']           
             }
            mood = {
                'UserId': mood['UserId'],
                'TenantId': mood['TenantId'],
                'SessionId': None,
                'ResourceId': mood['id'],
                'ResourceType': "symptom-how-do-you-feel",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User deleted mood record.",
                'Attributes': str(attributes),
                'Timestamp': mood['DeletedAt'],
                'UserRegistrationDate': mood['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(mood)
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
    def sync_mood_delete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            moods = MoodEventsSynchronizer.get_reancare_mood_delete_events(filters)
            if moods:
                for mood in moods:
                    existing_event = DataSynchronizer.get_existing_event(
                        mood['UserId'], mood['id'], EventType.SymptomDelete)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = MoodEventsSynchronizer.add_analytics_mood_delete_event(mood)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(mood)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Mood Delete Events found.")
        except Exception as error:
            print(f"Error syncing User Mood Delete Events: {error}")
    
    #endregion
