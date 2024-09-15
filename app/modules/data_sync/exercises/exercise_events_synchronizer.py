from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class ExerciseEventsSynchronizer:

    #region Add Symptom events

    @staticmethod
    def get_reancare_exercise_start_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND exercise.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                exercise.id,
                exercise.EhrId,
                exercise.PatientUserId as UserId,
                exercise.Provider,
                exercise.TerraSummaryId,
                exercise.Exercise,
                exercise.Description,               
                exercise.Category,
                exercise.CaloriesBurned,
                exercise.Intensity,
                exercise.ImageResourceId,
                exercise.StartTime,
                exercise.EndTime,               
                exercise.DurationInMin,
                exercise.PhysicalActivityQuestion,
                exercise.PhysicalActivityQuestionAns,
                exercise.CreatedAt,
                exercise.UpdatedAt,
                exercise.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from exercise_physical_activities as exercise
            JOIN users as user ON exercise.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Exercise Create Events:", error)
            return None

    @staticmethod
    def add_analytics_exercise_start_event(exercise):
        try:
            event_name = EventType.ExerciseStart.value
            event_category = EventCategory.Exercise.value
            event_subject = EventSubject.Exercise.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': exercise['EhrId'],
                'PatientUserId': exercise['UserId'],
                'Provider': exercise['Provider'],
                'TerraSummaryId': exercise['TerraSummaryId'],
                'Exercise': exercise['Exercise'],
                'Description': exercise['Description'],
                'Category': exercise['Category'],
                'CaloriesBurned': exercise['CaloriesBurned'],
                'Intensity': exercise['Intensity'],
                'ImageResourceId': exercise['ImageResourceId'],
                'StartTime': exercise['StartTime'],
                'EndTime': exercise['EndTime'],
                'DurationInMin': exercise['DurationInMin'],
                'PhysicalActivityQuestion': exercise['PhysicalActivityQuestion'],
                'PhysicalActivityQuestionAns': exercise['PhysicalActivityQuestionAns']
             }
            exercise = {
                'UserId': exercise['UserId'],
                'TenantId': exercise['TenantId'],
                'SessionId': None,
                'ResourceId': exercise['id'],
                'ResourceType': "exercise",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User added a exercise.",
                'Attributes': str(attributes),
                'Timestamp': exercise['CreatedAt'],
                'UserRegistrationDate': exercise['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(exercise)
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
    def sync_exercise_start_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            exercises = ExerciseEventsSynchronizer.get_reancare_exercise_start_events(filters)
            if exercises:
                for exercise in exercises:
                    existing_event = DataSynchronizer.get_existing_event(
                        exercise['UserId'], exercise['id'], EventType.ExerciseStart)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = ExerciseEventsSynchronizer.add_analytics_exercise_start_event(exercise)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(exercise)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Exercise Create Events found.")
        except Exception as error:
            print(f"Error syncing User Exercise Create Events: {error}")

    #endregion

    #region Update nutrition events

    @staticmethod
    def get_reancare_exercise_update_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND exercise.UpdatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                exercise.id,
                exercise.EhrId,
                exercise.PatientUserId as UserId,
                exercise.Provider,
                exercise.TerraSummaryId,
                exercise.Exercise,
                exercise.Description,               
                exercise.Category,
                exercise.CaloriesBurned,
                exercise.Intensity,
                exercise.ImageResourceId,
                exercise.StartTime,
                exercise.EndTime,               
                exercise.DurationInMin,
                exercise.PhysicalActivityQuestion,
                exercise.PhysicalActivityQuestionAns,
                exercise.CreatedAt,
                exercise.UpdatedAt,
                exercise.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from exercise_physical_activities as exercise
            JOIN users as user ON exercise.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                exercise.CreatedAt <> exercise.UpdatedAt
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Exercise Update Events:", error)
            return None

    @staticmethod
    def add_analytics_exercise_update_event(exercise):
        try:
            event_name = EventType.ExerciseUpdate.value
            event_category = EventCategory.Exercise.value
            event_subject = EventSubject.Exercise.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': exercise['EhrId'],
                'PatientUserId': exercise['UserId'],
                'Provider': exercise['Provider'],
                'TerraSummaryId': exercise['TerraSummaryId'],
                'Exercise': exercise['Exercise'],
                'Description': exercise['Description'],
                'Category': exercise['Category'],
                'CaloriesBurned': exercise['CaloriesBurned'],
                'Intensity': exercise['Intensity'],
                'ImageResourceId': exercise['ImageResourceId'],
                'StartTime': exercise['StartTime'],
                'EndTime': exercise['EndTime'],
                'DurationInMin': exercise['DurationInMin'],
                'PhysicalActivityQuestion': exercise['PhysicalActivityQuestion'],
                'PhysicalActivityQuestionAns': exercise['PhysicalActivityQuestionAns']
             }
            exercise = {
                'UserId': exercise['UserId'],
                'TenantId': exercise['TenantId'],
                'SessionId': None,
                'ResourceId': exercise['id'],
                'ResourceType': "exercise",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User added a exercise.",
                'Attributes': str(attributes),
                'Timestamp': exercise['UpdatedAt'],
                'UserRegistrationDate': exercise['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(exercise)
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
    def sync_exercise_update_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            exercises = ExerciseEventsSynchronizer.get_reancare_exercise_update_events(filters)
            if exercises:
                for exercise in exercises:
                    existing_event = DataSynchronizer.get_existing_event(
                        exercise['UserId'], exercise['id'], EventType.ExerciseUpdate)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = ExerciseEventsSynchronizer.add_analytics_exercise_update_event(exercise)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(exercise)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Exercise Update Events found.")
        except Exception as error:
            print(f"Error syncing User Exercise Update Events: {error}")

    #endregion

    #region Update Symptom events

    @staticmethod
    def get_reancare_exercise_complete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND exercise.EndTime between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                exercise.id,
                exercise.EhrId,
                exercise.PatientUserId as UserId,
                exercise.Provider,
                exercise.TerraSummaryId,
                exercise.Exercise,
                exercise.Description,               
                exercise.Category,
                exercise.CaloriesBurned,
                exercise.Intensity,
                exercise.ImageResourceId,
                exercise.StartTime,
                exercise.EndTime,               
                exercise.DurationInMin,
                exercise.PhysicalActivityQuestion,
                exercise.PhysicalActivityQuestionAns,
                exercise.CreatedAt,
                exercise.UpdatedAt,
                exercise.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from exercise_physical_activities as exercise
            JOIN users as user ON exercise.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                exercise.EndTime IS NOT null
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Exercise Complete Events:", error)
            return None

    @staticmethod
    def add_analytics_exercise_complete_event(exercise):
        try:
            event_name = EventType.ExerciseComplete.value
            event_category = EventCategory.Exercise.value
            event_subject = EventSubject.Exercise.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': exercise['EhrId'],
                'PatientUserId': exercise['UserId'],
                'Provider': exercise['Provider'],
                'TerraSummaryId': exercise['TerraSummaryId'],
                'Exercise': exercise['Exercise'],
                'Description': exercise['Description'],
                'Category': exercise['Category'],
                'CaloriesBurned': exercise['CaloriesBurned'],
                'Intensity': exercise['Intensity'],
                'ImageResourceId': exercise['ImageResourceId'],
                'StartTime': exercise['StartTime'],
                'EndTime': exercise['EndTime'],
                'DurationInMin': exercise['DurationInMin'],
                'PhysicalActivityQuestion': exercise['PhysicalActivityQuestion'],
                'PhysicalActivityQuestionAns': exercise['PhysicalActivityQuestionAns']
             }
            exercise = {
                'UserId': exercise['UserId'],
                'TenantId': exercise['TenantId'],
                'SessionId': None,
                'ResourceId': exercise['id'],
                'ResourceType': "exercise",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User completed a exercise.",
                'Attributes': str(attributes),
                'Timestamp': exercise['EndTime'],
                'UserRegistrationDate': exercise['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(exercise)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_exercise_complete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            exercises = ExerciseEventsSynchronizer.get_reancare_exercise_complete_events(filters)
            if exercises:
                for exercise in exercises:
                    existing_event = DataSynchronizer.get_existing_event(
                        exercise['UserId'], exercise['id'], EventType.ExerciseComplete)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = ExerciseEventsSynchronizer.add_analytics_exercise_complete_event(exercise)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(exercise)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Exercise Complete Events found.")
        except Exception as error:
            print(f"Error syncing User Exercise Complete Events: {error}")

    #endregion

    @staticmethod
    def get_reancare_exercise_cancel_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND exercise.DeletedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                exercise.id,
                exercise.EhrId,
                exercise.PatientUserId as UserId,
                exercise.Provider,
                exercise.TerraSummaryId,
                exercise.Exercise,
                exercise.Description,               
                exercise.Category,
                exercise.CaloriesBurned,
                exercise.Intensity,
                exercise.ImageResourceId,
                exercise.StartTime,
                exercise.EndTime,               
                exercise.DurationInMin,
                exercise.PhysicalActivityQuestion,
                exercise.PhysicalActivityQuestionAns,
                exercise.CreatedAt,
                exercise.UpdatedAt,
                exercise.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from exercise_physical_activities as exercise
            JOIN users as user ON exercise.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                exercise.DeletedAt IS NOT null
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Exercise Cancel Events:", error)
            return None

    @staticmethod
    def add_analytics_exercise_cancel_event(exercise):
        try:
            event_name = EventType.ExerciseCancel.value
            event_category = EventCategory.Exercise.value
            event_subject = EventSubject.Exercise.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': exercise['EhrId'],
                'PatientUserId': exercise['UserId'],
                'Provider': exercise['Provider'],
                'TerraSummaryId': exercise['TerraSummaryId'],
                'Exercise': exercise['Exercise'],
                'Description': exercise['Description'],
                'Category': exercise['Category'],
                'CaloriesBurned': exercise['CaloriesBurned'],
                'Intensity': exercise['Intensity'],
                'ImageResourceId': exercise['ImageResourceId'],
                'StartTime': exercise['StartTime'],
                'EndTime': exercise['EndTime'],
                'DurationInMin': exercise['DurationInMin'],
                'PhysicalActivityQuestion': exercise['PhysicalActivityQuestion'],
                'PhysicalActivityQuestionAns': exercise['PhysicalActivityQuestionAns']
             }
            exercise = {
                'UserId': exercise['UserId'],
                'TenantId': exercise['TenantId'],
                'SessionId': None,
                'ResourceId': exercise['id'],
                'ResourceType': "exercise",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User cancel a exercise.",
                'Attributes': str(attributes),
                'Timestamp': exercise['DeletedAt'],
                'UserRegistrationDate': exercise['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(exercise)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_exercise_cancel_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            exercises = ExerciseEventsSynchronizer.get_reancare_exercise_cancel_events(filters)
            if exercises:
                for exercise in exercises:
                    existing_event = DataSynchronizer.get_existing_event(
                        exercise['UserId'], exercise['id'], EventType.ExerciseCancel)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = ExerciseEventsSynchronizer.add_analytics_exercise_cancel_event(exercise)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(exercise)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Exercise Cancel Events found.")
        except Exception as error:
            print(f"Error syncing User Exercise Cancel Events: {error}")


    #endregion
