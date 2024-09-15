from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class GoalEventsSynchronizer:

    #region Add Symptom events

    @staticmethod
    def get_reancare_goal_create_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND goal.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                goal.id,
                goal.PatientUserId as UserId,
                goal.GoalAchieved,
                goal.GoalAbandoned,
                goal.ProviderEnrollmentId,
                goal.Provider,               
                goal.ProviderCareplanName,
                goal.ProviderCareplanCode,
                goal.ProviderGoalCode,
                goal.Title,
                goal.Sequence,
                goal.HealthPriorityId,               
                goal.StartedAt,
                goal.CompletedAt,
                goal.ScheduledEndDate,
                goal.CreatedAt,
                goal.UpdatedAt,
                goal.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from patient_goals as goal
            JOIN users as user ON goal.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Goal Create Events:", error)
            return None

    @staticmethod
    def add_analytics_goal_create_event(goal):
        try:
            event_name = EventType.GoalCreate.value
            event_category = EventCategory.Goals.value
            event_subject = EventSubject.Goal.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'PatientUserId': goal['UserId'],
                'GoalAchieved': goal['GoalAchieved'],
                'GoalAbandoned': goal['GoalAbandoned'],
                'ProviderEnrollmentId': goal['ProviderEnrollmentId'],
                'Provider': goal['Provider'],
                'ProviderCareplanName': goal['ProviderCareplanName'],
                'ProviderCareplanCode': goal['ProviderCareplanCode'],
                'ProviderGoalCode': goal['ProviderGoalCode'],
                'Title': goal['Title'],
                'Sequence': goal['Sequence'],
                'HealthPriorityId': goal['HealthPriorityId'],
                'StartedAt': goal['StartedAt'],
                'CompletedAt': goal['CompletedAt'],
                'ScheduledEndDate': goal['ScheduledEndDate']
             }
            goal = {
                'UserId': goal['UserId'],
                'TenantId': goal['TenantId'],
                'SessionId': None,
                'ResourceId': goal['id'],
                'ResourceType': "goal",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User added a goal.",
                'Attributes': str(attributes),
                'Timestamp': goal['CreatedAt'],
                'UserRegistrationDate': goal['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(goal)
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
    def sync_goal_create_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            goals = GoalEventsSynchronizer.get_reancare_goal_create_events(filters)
            if goals:
                for goal in goals:
                    existing_event = DataSynchronizer.get_existing_event(
                        goal['UserId'], goal['id'], EventType.GoalCreate)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = GoalEventsSynchronizer.add_analytics_goal_create_event(goal)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(goal)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Goal Create Events found.")
        except Exception as error:
            print(f"Error syncing User Goal Create Events: {error}")

    #endregion

    #region Update nutrition events

    @staticmethod
    def get_reancare_goal_update_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND goal.UpdatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                goal.id,
                goal.PatientUserId as UserId,
                goal.GoalAchieved,
                goal.GoalAbandoned,
                goal.ProviderEnrollmentId,
                goal.Provider,               
                goal.ProviderCareplanName,
                goal.ProviderCareplanCode,
                goal.ProviderGoalCode,
                goal.Title,
                goal.Sequence,
                goal.HealthPriorityId,               
                goal.StartedAt,
                goal.CompletedAt,
                goal.ScheduledEndDate,
                goal.CreatedAt,
                goal.UpdatedAt,
                goal.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from patient_goals as goal
            JOIN users as user ON goal.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                goal.CreatedAt <> goal.UpdatedAt
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Goal Update Events:", error)
            return None

    @staticmethod
    def add_analytics_goal_update_event(goal):
        try:
            event_name = EventType.GoalUpdate.value
            event_category = EventCategory.Goals.value
            event_subject = EventSubject.Goal.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'PatientUserId': goal['UserId'],
                'GoalAchieved': goal['GoalAchieved'],
                'GoalAbandoned': goal['GoalAbandoned'],
                'ProviderEnrollmentId': goal['ProviderEnrollmentId'],
                'Provider': goal['Provider'],
                'ProviderCareplanName': goal['ProviderCareplanName'],
                'ProviderCareplanCode': goal['ProviderCareplanCode'],
                'ProviderGoalCode': goal['ProviderGoalCode'],
                'Title': goal['Title'],
                'Sequence': goal['Sequence'],
                'HealthPriorityId': goal['HealthPriorityId'],
                'StartedAt': goal['StartedAt'],
                'CompletedAt': goal['CompletedAt'],
                'ScheduledEndDate': goal['ScheduledEndDate']
             }
            goal = {
                'UserId': goal['UserId'],
                'TenantId': goal['TenantId'],
                'SessionId': None,
                'ResourceId': goal['id'],
                'ResourceType': "goal",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User updated a goal.",
                'Attributes': str(attributes),
                'Timestamp': goal['UpdatedAt'],
                'UserRegistrationDate': goal['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(goal)
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
    def sync_goal_update_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            goals = GoalEventsSynchronizer.get_reancare_goal_update_events(filters)
            if goals:
                for goal in goals:
                    existing_event = DataSynchronizer.get_existing_event(
                        goal['UserId'], goal['id'], EventType.GoalUpdate)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = GoalEventsSynchronizer.add_analytics_goal_update_event(goal)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(goal)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Goal Update Events found.")
        except Exception as error:
            print(f"Error syncing User Goal Update Events: {error}")

    #endregion

    @staticmethod
    def get_reancare_goal_start_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND goal.StartedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                goal.id,
                goal.PatientUserId as UserId,
                goal.GoalAchieved,
                goal.GoalAbandoned,
                goal.ProviderEnrollmentId,
                goal.Provider,               
                goal.ProviderCareplanName,
                goal.ProviderCareplanCode,
                goal.ProviderGoalCode,
                goal.Title,
                goal.Sequence,
                goal.HealthPriorityId,               
                goal.StartedAt,
                goal.CompletedAt,
                goal.ScheduledEndDate,
                goal.CreatedAt,
                goal.UpdatedAt,
                goal.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from patient_goals as goal
            JOIN users as user ON goal.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                goal.StartedAt IS NOT null
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Goal Start Events:", error)
            return None

    @staticmethod
    def add_analytics_goal_start_event(goal):
        try:
            event_name = EventType.GoalStart.value
            event_category = EventCategory.Goals.value
            event_subject = EventSubject.Goal.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'PatientUserId': goal['UserId'],
                'GoalAchieved': goal['GoalAchieved'],
                'GoalAbandoned': goal['GoalAbandoned'],
                'ProviderEnrollmentId': goal['ProviderEnrollmentId'],
                'Provider': goal['Provider'],
                'ProviderCareplanName': goal['ProviderCareplanName'],
                'ProviderCareplanCode': goal['ProviderCareplanCode'],
                'ProviderGoalCode': goal['ProviderGoalCode'],
                'Title': goal['Title'],
                'Sequence': goal['Sequence'],
                'HealthPriorityId': goal['HealthPriorityId'],
                'StartedAt': goal['StartedAt'],
                'CompletedAt': goal['CompletedAt'],
                'ScheduledEndDate': goal['ScheduledEndDate']
             }
            goal = {
                'UserId': goal['UserId'],
                'TenantId': goal['TenantId'],
                'SessionId': None,
                'ResourceId': goal['id'],
                'ResourceType': "goal",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User started a goal.",
                'Attributes': str(attributes),
                'Timestamp': goal['StartedAt'],
                'UserRegistrationDate': goal['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(goal)
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
    def sync_goal_start_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            goals = GoalEventsSynchronizer.get_reancare_goal_start_events(filters)
            if goals:
                for goal in goals:
                    existing_event = DataSynchronizer.get_existing_event(
                        goal['UserId'], goal['id'], EventType.GoalStart)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = GoalEventsSynchronizer.add_analytics_goal_start_event(goal)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(goal)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Goal Start Events found.")
        except Exception as error:
            print(f"Error syncing User Goal Start Events: {error}")

    #endregion

    @staticmethod
    def get_reancare_goal_complete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND goal.CompletedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                goal.id,
                goal.PatientUserId as UserId,
                goal.GoalAchieved,
                goal.GoalAbandoned,
                goal.ProviderEnrollmentId,
                goal.Provider,               
                goal.ProviderCareplanName,
                goal.ProviderCareplanCode,
                goal.ProviderGoalCode,
                goal.Title,
                goal.Sequence,
                goal.HealthPriorityId,               
                goal.StartedAt,
                goal.CompletedAt,
                goal.ScheduledEndDate,
                goal.CreatedAt,
                goal.UpdatedAt,
                goal.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from patient_goals as goal
            JOIN users as user ON goal.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                goal.CompletedAt IS NOT null
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Goal Complete Events:", error)
            return None

    @staticmethod
    def add_analytics_goal_complete_event(goal):
        try:
            event_name = EventType.GoalComplete.value
            event_category = EventCategory.Goals.value
            event_subject = EventSubject.Goal.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'PatientUserId': goal['UserId'],
                'GoalAchieved': goal['GoalAchieved'],
                'GoalAbandoned': goal['GoalAbandoned'],
                'ProviderEnrollmentId': goal['ProviderEnrollmentId'],
                'Provider': goal['Provider'],
                'ProviderCareplanName': goal['ProviderCareplanName'],
                'ProviderCareplanCode': goal['ProviderCareplanCode'],
                'ProviderGoalCode': goal['ProviderGoalCode'],
                'Title': goal['Title'],
                'Sequence': goal['Sequence'],
                'HealthPriorityId': goal['HealthPriorityId'],
                'StartedAt': goal['StartedAt'],
                'CompletedAt': goal['CompletedAt'],
                'ScheduledEndDate': goal['ScheduledEndDate']
             }
            goal = {
                'UserId': goal['UserId'],
                'TenantId': goal['TenantId'],
                'SessionId': None,
                'ResourceId': goal['id'],
                'ResourceType': "goal",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User completed a goal.",
                'Attributes': str(attributes),
                'Timestamp': goal['CompletedAt'],
                'UserRegistrationDate': goal['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(goal)
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
    def sync_goal_complete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            goals = GoalEventsSynchronizer.get_reancare_goal_complete_events(filters)
            if goals:
                for goal in goals:
                    existing_event = DataSynchronizer.get_existing_event(
                        goal['UserId'], goal['id'], EventType.GoalComplete)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = GoalEventsSynchronizer.add_analytics_goal_complete_event(goal)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(goal)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Goal Complete Events found.")
        except Exception as error:
            print(f"Error syncing User Goal Complete Events: {error}")

    #endregion

    @staticmethod
    def get_reancare_goal_cancel_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND goal.DeletedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                goal.id,
                goal.PatientUserId as UserId,
                goal.GoalAchieved,
                goal.GoalAbandoned,
                goal.ProviderEnrollmentId,
                goal.Provider,               
                goal.ProviderCareplanName,
                goal.ProviderCareplanCode,
                goal.ProviderGoalCode,
                goal.Title,
                goal.Sequence,
                goal.HealthPriorityId,               
                goal.StartedAt,
                goal.CompletedAt,
                goal.ScheduledEndDate,
                goal.CreatedAt,
                goal.UpdatedAt,
                goal.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from patient_goals as goal
            JOIN users as user ON goal.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                goal.DeletedAt IS NOT null
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Goal Cancel Events:", error)
            return None

    @staticmethod
    def add_analytics_goal_cancel_event(goal):
        try:
            event_name = EventType.GoalCancel.value
            event_category = EventCategory.Goals.value
            event_subject = EventSubject.Goal.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'PatientUserId': goal['UserId'],
                'GoalAchieved': goal['GoalAchieved'],
                'GoalAbandoned': goal['GoalAbandoned'],
                'ProviderEnrollmentId': goal['ProviderEnrollmentId'],
                'Provider': goal['Provider'],
                'ProviderCareplanName': goal['ProviderCareplanName'],
                'ProviderCareplanCode': goal['ProviderCareplanCode'],
                'ProviderGoalCode': goal['ProviderGoalCode'],
                'Title': goal['Title'],
                'Sequence': goal['Sequence'],
                'HealthPriorityId': goal['HealthPriorityId'],
                'StartedAt': goal['StartedAt'],
                'CompletedAt': goal['CompletedAt'],
                'ScheduledEndDate': goal['ScheduledEndDate']
             }
            goal = {
                'UserId': goal['UserId'],
                'TenantId': goal['TenantId'],
                'SessionId': None,
                'ResourceId': goal['id'],
                'ResourceType': "goal",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User deleted a goal.",
                'Attributes': str(attributes),
                'Timestamp': goal['DeletedAt'],
                'UserRegistrationDate': goal['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(goal)
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
    def sync_goal_cancel_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            goals = GoalEventsSynchronizer.get_reancare_goal_cancel_events(filters)
            if goals:
                for goal in goals:
                    existing_event = DataSynchronizer.get_existing_event(
                        goal['UserId'], goal['id'], EventType.GoalCancel)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = GoalEventsSynchronizer.add_analytics_goal_cancel_event(goal)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(goal)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Goal Cancel Events found.")
        except Exception as error:
            print(f"Error syncing User Goal Cancel Events: {error}")

    #endregion
