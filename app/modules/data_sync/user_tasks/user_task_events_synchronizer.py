from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class UserTaskEventsSynchronizer:

    #region User Task Start events

    @staticmethod
    def get_reancare_user_task_start_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND userTask.StartedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                userTask.id,
                userTask.UserId,
                userTask.DisplayId,
                userTask.Task,
                userTask.Category,
                userTask.Description,
                userTask.ActionType,
                userTask.ActionId,
                userTask.ScheduledStartTime,
                userTask.ScheduledEndTime,
                userTask.TenantName,
                userTask.Channel,
                userTask.Started,
                userTask.StartedAt,
                userTask.Finished,
                userTask.FinishedAt,
                userTask.Cancelled,
                userTask.CancelledAt,
                userTask.CancellationReason,
                userTask.IsRecurrent,
                userTask.RecurrenceScheduleId,
                userTask.CreatedAt,
                userTask.UpdatedAt,
                userTask.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            FROM user_tasks AS userTask
            JOIN users as user ON userTask.UserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                userTask.StartedAt IS NOT null
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Task Start Events:", error)
            return None

    @staticmethod
    def add_analytics_user_task_start_event(user_task):
        try:
            event_name = EventType.UserTaskStart.value
            event_category = EventCategory.UserTask.value
            event_subject = user_task['Category']
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'DisplayId': user_task['DisplayId'],
                'Task': user_task['Task'],
                'Category': user_task['Category'],
                'Description': user_task['Description'],
                'ActionType': user_task['ActionType'],
                'ActionId': user_task['ActionId'],
                'ScheduledStartTime': user_task['ScheduledStartTime'],
                'ScheduledEndTime': user_task['ScheduledEndTime'],
                'TenantName': user_task['TenantName'],
                'Channel': user_task['Channel'],
                'Started': user_task['Started'],
                'StartedAt': user_task['StartedAt'],
                'Finished': user_task['Finished'],
                'FinishedAt': user_task['FinishedAt'],
                'Cancelled': user_task['Cancelled'],
                'CancelledAt': user_task['CancelledAt'],
                'CancellationReason': user_task['CancellationReason'],
                'IsRecurrent': user_task['IsRecurrent'],
                'RecurrenceScheduleId': user_task['RecurrenceScheduleId']
            }
            user_task = {
                'UserId': user_task['UserId'],
                'TenantId': user_task['TenantId'],
                'SessionId': None,
                'ResourceId': user_task['id'],
                'ResourceType': "user-task",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User task is started.",
                'Attributes': str(attributes),
                'Timestamp': user_task['StartedAt'],
                'UserRegistrationDate': user_task['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(user_task)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_user_task_start_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            user_tasks = UserTaskEventsSynchronizer.get_reancare_user_task_start_events(filters)
            if user_tasks:
                for user_task in user_tasks:
                    existing_event = DataSynchronizer.get_existing_event(
                        user_task['UserId'], user_task['id'], EventType.UserTaskStart)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = UserTaskEventsSynchronizer.add_analytics_user_task_start_event(user_task)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(user_task)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User User Task Start Events found.")
        except Exception as error:
            print(f"Error syncing User User Task Start Events: {error}")

    #endregion

    #region Start User Task Complete events

    @staticmethod
    def get_reancare_user_task_complete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND userTask.FinishedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                userTask.id,
                userTask.UserId,
                userTask.DisplayId,
                userTask.Task,
                userTask.Category,
                userTask.Description,
                userTask.ActionType,
                userTask.ActionId,
                userTask.ScheduledStartTime,
                userTask.ScheduledEndTime,
                userTask.TenantName,
                userTask.Channel,
                userTask.Started,
                userTask.StartedAt,
                userTask.Finished,
                userTask.FinishedAt,
                userTask.Cancelled,
                userTask.CancelledAt,
                userTask.CancellationReason,
                userTask.IsRecurrent,
                userTask.RecurrenceScheduleId,
                userTask.CreatedAt,
                userTask.UpdatedAt,
                userTask.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            FROM user_tasks AS userTask
            JOIN users as user ON userTask.UserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                userTask.FinishedAt IS NOT null
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Task Complete Events:", error)
            return None

    @staticmethod
    def add_analytics_user_task_complete_event(user_task):
        try:
            event_name = EventType.UserTaskComplete.value
            event_category = EventCategory.UserTask.value
            event_subject = user_task['Category']
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'DisplayId': user_task['DisplayId'],
                'Task': user_task['Task'],
                'Category': user_task['Category'],
                'Description': user_task['Description'],
                'ActionType': user_task['ActionType'],
                'ActionId': user_task['ActionId'],
                'ScheduledStartTime': user_task['ScheduledStartTime'],
                'ScheduledEndTime': user_task['ScheduledEndTime'],
                'TenantName': user_task['TenantName'],
                'Channel': user_task['Channel'],
                'Started': user_task['Started'],
                'StartedAt': user_task['StartedAt'],
                'Finished': user_task['Finished'],
                'FinishedAt': user_task['FinishedAt'],
                'Cancelled': user_task['Cancelled'],
                'CancelledAt': user_task['CancelledAt'],
                'CancellationReason': user_task['CancellationReason'],
                'IsRecurrent': user_task['IsRecurrent'],
                'RecurrenceScheduleId': user_task['RecurrenceScheduleId']
            }
            user_task = {
                 'UserId': user_task['UserId'],
                'TenantId': user_task['TenantId'],
                'SessionId': None,
                'ResourceId': user_task['id'],
                'ResourceType': "user-task",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User task is completed.",
                'Attributes': str(attributes),
                'Timestamp': user_task['FinishedAt'],
                'UserRegistrationDate': user_task['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(user_task)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_user_task_complete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            user_tasks = UserTaskEventsSynchronizer.get_reancare_user_task_complete_events(filters)
            if user_tasks:
                for user_task in user_tasks:
                    existing_event = DataSynchronizer.get_existing_event(
                        user_task['UserId'], user_task['id'], EventType.UserTaskComplete)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = UserTaskEventsSynchronizer.add_analytics_user_task_complete_event(user_task)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(user_task)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User User Task Complete Events found.")
        except Exception as error:
            print(f"Error syncing User Task Complete Events: {error}")

    #endregion

    #region Start User Task Cancel events

    @staticmethod
    def get_reancare_user_task_cancel_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND userTask.CancelledAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                userTask.id,
                userTask.UserId,
                userTask.DisplayId,
                userTask.Task,
                userTask.Category,
                userTask.Description,
                userTask.ActionType,
                userTask.ActionId,
                userTask.ScheduledStartTime,
                userTask.ScheduledEndTime,
                userTask.TenantName,
                userTask.Channel,
                userTask.Started,
                userTask.StartedAt,
                userTask.Finished,
                userTask.FinishedAt,
                userTask.Cancelled,
                userTask.CancelledAt,
                userTask.CancellationReason,
                userTask.IsRecurrent,
                userTask.RecurrenceScheduleId,
                userTask.CreatedAt,
                userTask.UpdatedAt,
                userTask.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            FROM user_tasks AS userTask
            JOIN users as user ON userTask.UserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                userTask.CancelledAt IS NOT null
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Task Cancel Events:", error)
            return None

    @staticmethod
    def add_analytics_user_task_cancel_event(user_task):
        try:
            event_name = EventType.UserTaskCancel.value
            event_category = EventCategory.UserTask.value
            event_subject = user_task['Category']
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'DisplayId': user_task['DisplayId'],
                'Task': user_task['Task'],
                'Category': user_task['Category'],
                'Description': user_task['Description'],
                'ActionType': user_task['ActionType'],
                'ActionId': user_task['ActionId'],
                'ScheduledStartTime': user_task['ScheduledStartTime'],
                'ScheduledEndTime': user_task['ScheduledEndTime'],
                'TenantName': user_task['TenantName'],
                'Channel': user_task['Channel'],
                'Started': user_task['Started'],
                'StartedAt': user_task['StartedAt'],
                'Finished': user_task['Finished'],
                'FinishedAt': user_task['FinishedAt'],
                'Cancelled': user_task['Cancelled'],
                'CancelledAt': user_task['CancelledAt'],
                'CancellationReason': user_task['CancellationReason'],
                'IsRecurrent': user_task['IsRecurrent'],
                'RecurrenceScheduleId': user_task['RecurrenceScheduleId']
            }
            user_task = {
                 'UserId': user_task['UserId'],
                'TenantId': user_task['TenantId'],
                'SessionId': None,
                'ResourceId': user_task['id'],
                'ResourceType': "user-task",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User task is completed.",
                'Attributes': str(attributes),
                'Timestamp': user_task['CancelledAt'],
                'UserRegistrationDate': user_task['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(user_task)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_user_task_cancel_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            user_tasks = UserTaskEventsSynchronizer.get_reancare_user_task_cancel_events(filters)
            if user_tasks:
                for user_task in user_tasks:
                    existing_event = DataSynchronizer.get_existing_event(
                        user_task['UserId'], user_task['id'], EventType.UserTaskCancel)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = UserTaskEventsSynchronizer.add_analytics_user_task_cancel_event(user_task)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(user_task)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User User Task Cancel Events found.")
        except Exception as error:
            print(f"Error syncing User Task Cancel Events: {error}")

    #endregion
