from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class CareplanEventsSynchronizer:

    #region Careplan Enrollment events

    @staticmethod
    def get_reancare_careplan_enroll_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND careplanEnrollment.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                careplanEnrollment.id,
                careplanEnrollment.PatientUserId as UserId,
                careplanEnrollment.EnrollmentId,
                careplanEnrollment.ParticipantId,
                careplanEnrollment.Provider,
                careplanEnrollment.PlanCode,
                careplanEnrollment.PlanName,
                careplanEnrollment.StartDate,
                careplanEnrollment.EndDate,
                careplanEnrollment.IsActive,
                careplanEnrollment.Name,
                careplanEnrollment.HasHighRisk,
                careplanEnrollment.Complication,
                careplanEnrollment.ParticipantStringId,
                careplanEnrollment.EnrollmentStringId,
                careplanEnrollment.CreatedAt,
                careplanEnrollment.UpdatedAt,
                careplanEnrollment.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from careplan_enrollments as careplanEnrollment
            JOIN users as user ON careplanEnrollment.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Careplan Enrollment Events:", error)
            return None

    @staticmethod
    def add_analytics_careplan_enroll_event(careplan_enrollment):
        try:
            event_name = EventType.CareplanEnrollment.value
            event_category = EventCategory.Careplan.value
            event_subject = EventSubject.CareplanEnrollment.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'PatientUserId' : careplan_enrollment['UserId'],
                'Provider'      : careplan_enrollment['Provider'],
                'PlanName'      : careplan_enrollment['PlanName'],
                'PlanCode'      : careplan_enrollment['PlanCode'],
                'StartDate'     : careplan_enrollment['StartDate'],
                'EndDate'       : careplan_enrollment['EndDate']
                # 'EnrollmentId': careplan_enrollment['EnrollmentId'],
                # 'ParticipantId': careplan_enrollment['ParticipantId'],
                # 'Provider': careplan_enrollment['Provider'],
                # 'PlanCode': careplan_enrollment['PlanCode'],
                # 'PlanName': careplan_enrollment['PlanName'],
                # 'StartDate': careplan_enrollment['StartDate'],
                # 'EndDate': careplan_enrollment['EndDate'],
                # 'IsActive': careplan_enrollment['IsActive'],
                # 'Name': careplan_enrollment['Name'],
                # 'HasHighRisk': careplan_enrollment['HasHighRisk'],
                # 'Complication': careplan_enrollment['Complication'],
                # 'ParticipantStringId': careplan_enrollment['ParticipantStringId'],
                # 'EnrollmentStringId': careplan_enrollment['EnrollmentStringId'],
            }
            careplan_enrollment = {
                'UserId': careplan_enrollment['UserId'],
                'TenantId': careplan_enrollment['TenantId'],
                'SessionId': None,
                'ResourceId': careplan_enrollment['id'],
                'ResourceType': "Careplan",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User enrolled to careplan.",
                'Attributes': str(attributes),
                'Timestamp': careplan_enrollment['CreatedAt'],
                'UserRegistrationDate': careplan_enrollment['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(careplan_enrollment)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_careplan_enroll_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            careplan_enrollments = CareplanEventsSynchronizer.get_reancare_careplan_enroll_events(filters)
            if careplan_enrollments:
                for careplan_enrollment in careplan_enrollments:
                    existing_event = DataSynchronizer.get_existing_event(
                        careplan_enrollment['UserId'], careplan_enrollment['id'], EventType.CareplanEnrollment)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = CareplanEventsSynchronizer.add_analytics_careplan_enroll_event(careplan_enrollment)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(careplan_enrollment)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Careplan Enrollment Events found.")
        except Exception as error:
            print(f"Error syncing User Careplan Enrollment Events: {error}")

    #endregion

    #region Start Assessment events

    # @staticmethod
    # def get_reancare_careplan_start_events(filters: DataSyncSearchFilter):
    #     try:
    #         selection_condition = f"AND careplanEnrollment.StartDate between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
    #         rean_db_connector = get_reancare_db_connector()
    #         query = f"""
    #         SELECT
    #             careplanEnrollment.id,
    #             careplanEnrollment.PatientUserId as UserId,
    #             careplanEnrollment.EnrollmentId,
    #             careplanEnrollment.ParticipantId,
    #             careplanEnrollment.Provider,
    #             careplanEnrollment.PlanCode,
    #             careplanEnrollment.PlanName,
    #             careplanEnrollment.StartDate,
    #             careplanEnrollment.EndDate,
    #             careplanEnrollment.IsActive,
    #             careplanEnrollment.Name,
    #             careplanEnrollment.HasHighRisk,
    #             careplanEnrollment.Complication,
    #             careplanEnrollment.ParticipantStringId,
    #             careplanEnrollment.EnrollmentStringId,
    #             careplanEnrollment.CreatedAt,
    #             careplanEnrollment.UpdatedAt,
    #             careplanEnrollment.DeletedAt,
    #             user.id as UserId,
    #             user.TenantId as TenantId,
    #             user.CreatedAt as UserRegistrationDate
    #         from careplan_enrollments as careplanEnrollment
    #         JOIN users as user ON careplanEnrollment.PatientUserId = user.id
    #         WHERE
    #             user.IsTestUser = 0
    #             {selection_condition}
    #         """
    #         rows = rean_db_connector.execute_read_query(query)
    #         return rows
    #     except Exception as error:
    #         print("Error retrieving User Careplan Start Events:", error)
    #         return None

    # @staticmethod
    # def add_analytics_careplan_start_event(careplan_enrollment):
    #     try:
    #         event_name = EventType.CareplanStart.value
    #         event_category = EventCategory.Careplan.value
    #         event_subject = EventSubject.Careplan.value
    #         # user = DataSynchronizer.get_user(medication['UserId'])
    #         # if not user:
    #         #     print(f"User not found for the event: {medication}")
    #         #     return None
    #         attributes = {
    #             'EnrollmentId': careplan_enrollment['EnrollmentId'],
    #             'ParticipantId': careplan_enrollment['ParticipantId'],
    #             'Provider': careplan_enrollment['Provider'],
    #             'PlanCode': careplan_enrollment['PlanCode'],
    #             'PlanName': careplan_enrollment['PlanName'],
    #             'StartDate': careplan_enrollment['StartDate'],
    #             'EndDate': careplan_enrollment['EndDate'],
    #             'IsActive': careplan_enrollment['IsActive'],
    #             'Name': careplan_enrollment['Name'],
    #             'HasHighRisk': careplan_enrollment['HasHighRisk'],
    #             'Complication': careplan_enrollment['Complication'],
    #             'ParticipantStringId': careplan_enrollment['ParticipantStringId'],
    #             'EnrollmentStringId': careplan_enrollment['EnrollmentStringId']
    #         }
    #         careplan_enrollment = {
    #             'UserId': careplan_enrollment['UserId'],
    #             'TenantId': careplan_enrollment['TenantId'],
    #             'SessionId': None,
    #             'ResourceId': careplan_enrollment['id'],
    #             'ResourceType': "Careplan",
    #             'SourceName': "ReanCare",
    #             'SourceVersion': "Unknown",
    #             'EventName': event_name,
    #             'EventSubject': event_subject,
    #             'EventCategory': event_category,
    #             'ActionType': "User-Action",
    #             'ActionStatement': "User start the careplan.",
    #             'Attributes': str(attributes),
    #             'Timestamp': careplan_enrollment['StartDate'],
    #             'UserRegistrationDate': careplan_enrollment['UserRegistrationDate']
    #         }
    #         new_event_added = DataSynchronizer.add_event(careplan_enrollment)
    #         if not new_event_added:
    #             print(f"Not inserted data.")
    #             return None
    #         else:
    #             return new_event_added
    #     except mysql.connector.Error as error:
    #         print(f"Failed to insert event: {error}")
    #         return None

    # @staticmethod
    # def sync_careplan_start_events(filters: DataSyncSearchFilter):
    #     try:
    #         existing_event_count = 0
    #         synched_event_count = 0
    #         event_not_synched = []
    #         careplan_enrollments = CareplanEventsSynchronizer.get_reancare_careplan_start_events(filters)
    #         if careplan_enrollments:
    #             for careplan_enrollment in careplan_enrollments:
    #                 existing_event = DataSynchronizer.get_existing_event(
    #                     careplan_enrollment['UserId'], careplan_enrollment['id'], EventType.CareplanStart)
    #                 if existing_event is not None:
    #                     existing_event_count += 1
    #                 else:
    #                     new_event = CareplanEventsSynchronizer.add_analytics_careplan_start_event(careplan_enrollment)
    #                     if new_event:
    #                         synched_event_count += 1
    #                     else:
    #                         event_not_synched.append(careplan_enrollment)
    #             print(f"Existing Event Count: {existing_event_count}")
    #             print(f"Synched Event Count: {synched_event_count}")
    #             print(f"Event Not Synched: {event_not_synched}")
    #         else:
    #             print(f"No User Careplan Start Events found.")
    #     except Exception as error:
    #         print(f"Error syncing User Careplan Start Events: {error}")

    #endregion
    #region Complete Assessment events

    @staticmethod
    def get_reancare_careplan_complete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND careplanEnrollment.EndDate between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                careplanEnrollment.id,
                careplanEnrollment.PatientUserId as UserId,
                careplanEnrollment.EnrollmentId,
                careplanEnrollment.ParticipantId,
                careplanEnrollment.Provider,
                careplanEnrollment.PlanCode,
                careplanEnrollment.PlanName,
                careplanEnrollment.StartDate,
                careplanEnrollment.EndDate,
                careplanEnrollment.IsActive,
                careplanEnrollment.Name,
                careplanEnrollment.HasHighRisk,
                careplanEnrollment.Complication,
                careplanEnrollment.ParticipantStringId,
                careplanEnrollment.EnrollmentStringId,
                careplanEnrollment.CreatedAt,
                careplanEnrollment.UpdatedAt,
                careplanEnrollment.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from careplan_enrollments as careplanEnrollment
            JOIN users as user ON careplanEnrollment.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Assessment Complete Events:", error)
            return None

    @staticmethod
    def add_analytics_careplan_complete_event(careplan_enrollment):
        try:
            event_name = EventType.CareplanComplete.value
            event_category = EventCategory.Careplan.value
            event_subject = EventSubject.CareplanEnrollment.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'PatientUserId' : careplan_enrollment['UserId'],
                'Provider'      : careplan_enrollment['Provider'],
                'PlanName'      : careplan_enrollment['PlanName'],
                'PlanCode'      : careplan_enrollment['PlanCode'],
                'StartDate'     : careplan_enrollment['StartDate'],
                'EndDate'       : careplan_enrollment['EndDate'],
                'StoppedAt'     : careplan_enrollment['DeletedAt'],
                # 'EnrollmentId': careplan_enrollment['EnrollmentId'],
                # 'ParticipantId': careplan_enrollment['ParticipantId'],
                # 'Provider': careplan_enrollment['Provider'],
                # 'PlanCode': careplan_enrollment['PlanCode'],
                # 'PlanName': careplan_enrollment['PlanName'],
                # 'StartDate': careplan_enrollment['StartDate'],
                # 'EndDate': careplan_enrollment['EndDate'],
                # 'IsActive': careplan_enrollment['IsActive'],
                # 'Name': careplan_enrollment['Name'],
                # 'HasHighRisk': careplan_enrollment['HasHighRisk'],
                # 'Complication': careplan_enrollment['Complication'],
                # 'ParticipantStringId': careplan_enrollment['ParticipantStringId'],
                # 'EnrollmentStringId': careplan_enrollment['EnrollmentStringId']
            }
            careplan_enrollment = {
                'UserId': careplan_enrollment['UserId'],
                'TenantId': careplan_enrollment['TenantId'],
                'SessionId': None,
                'ResourceId': careplan_enrollment['id'],
                'ResourceType': "careplan-enrollment",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User completed the careplan.",
                'Attributes': str(attributes),
                'Timestamp': careplan_enrollment['EndDate'],
                'UserRegistrationDate': careplan_enrollment['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(careplan_enrollment)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_careplan_complete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            careplan_enrollments = CareplanEventsSynchronizer.get_reancare_careplan_complete_events(filters)
            if careplan_enrollments:
                for careplan_enrollment in careplan_enrollments:
                    existing_event = DataSynchronizer.get_existing_event(
                        careplan_enrollment['UserId'], careplan_enrollment['id'], EventType.CareplanComplete)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = CareplanEventsSynchronizer.add_analytics_careplan_complete_event(careplan_enrollment)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(careplan_enrollment)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Careplan Complete Events found.")
        except Exception as error:
            print(f"Error syncing User Careplan Complete Events: {error}")

    #endregion

    #region Careplan Task Start events

    # @staticmethod
    # def get_reancare_careplan_task_start_events(filters: DataSyncSearchFilter):
    #     try:
    #         selection_condition = f"AND user_task.StartedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
    #         rean_db_connector = get_reancare_db_connector()
    #         query = f"""
    #         select 
    #             careplan_activity.id,
    #             careplan_activity.PatientUserId as UserId,
    #             careplan_activity.UserTaskId,
    #             careplan_activity.ProviderActionId,
    #             careplan_activity.EnrollmentId,
    #             careplan_activity.Provider,
    #             careplan_activity.PlanName,
    #             careplan_activity.PlanCode,
    #             careplan_activity.Type,
    #             careplan_activity.Category,
    #             careplan_activity.Title,
    #             careplan_activity.Description,
    #             careplan_activity.Transcription,
    #             careplan_activity.Url,
    #             careplan_activity.Language,
    #             careplan_activity.ScheduledAt,
    #             user_task.StartedAt,
    #             user_task.FinishedAt,
    #             careplan_activity.Sequence,
    #             careplan_activity.Frequency,
    #             careplan_activity.Status, 
    #             careplan_activity.UserResponse,
    #             careplan_activity.RawContent,
    #             careplan_activity.CreatedAt,
    #             careplan_activity.UpdatedAt,
    #             careplan_activity.DeletedAt,
    #             user.id as UserId,
    #             user.TenantId as TenantId,
    #             user.CreatedAt as UserRegistrationDate
    #         FROM careplan_activities AS careplan_activity
    #         JOIN user_tasks as user_task ON user_task.ActionId = careplan_activity.id
    #         JOIN users as user ON careplan_activity.PatientUserId = user.id
    #         WHERE
    #             user.IsTestUser = 0
    #             AND
    #             user_task.StartedAt IS NOT null
    #             {selection_condition}
    #         """
    #         rows = rean_db_connector.execute_read_query(query)
    #         return rows
    #     except Exception as error:
    #         print("Error retrieving User Careplan Task Start Events:", error)
    #         return None

    # @staticmethod
    # def add_analytics_careplan_task_start_event(careplan_task):
    #     try:
    #         event_name = EventType.CareplanTaskStart.value
    #         event_category = EventCategory.CareplanTask.value
    #         event_subject = EventSubject.CareplanTask.value
    #         # user = DataSynchronizer.get_user(medication['UserId'])
    #         # if not user:
    #         #     print(f"User not found for the event: {medication}")
    #         #     return None
    #         attributes = {
    #             'UserTaskId': careplan_task['UserTaskId'],
    #             'ProviderActionId': careplan_task['ProviderActionId'],
    #             'EnrollmentId': careplan_task['EnrollmentId'],
    #             'Provider': careplan_task['Provider'],
    #             'PlanName': careplan_task['PlanName'],
    #             'PlanCode': careplan_task['PlanCode'],
    #             'Type': careplan_task['Type'],
    #             'Category': careplan_task['Category'],
    #              'Title': careplan_task['Title'],
    #             'Description': careplan_task['Description'],
    #             'Transcription': careplan_task['Transcription'],
    #             'Url': careplan_task['Url'],
    #             'Language': careplan_task['Language'],
    #             'ScheduledAt': careplan_task['ScheduledAt'],
    #             'StartedAt': careplan_task['StartedAt'],
    #             'FinishedAt': careplan_task['FinishedAt'],
    #             'Sequence': careplan_task['Sequence'],
    #             'Frequency': careplan_task['Frequency'],
    #             'Status': careplan_task['Status'],
    #             'UserResponse': careplan_task['UserResponse'],
    #             'RawContent': careplan_task['RawContent'],
    #         }
    #         careplan_task = {
    #             'UserId': careplan_task['UserId'],
    #             'TenantId': careplan_task['TenantId'],
    #             'SessionId': None,
    #             'ResourceId': careplan_task['id'],
    #             'ResourceType': "Careplan-Task",
    #             'SourceName': "ReanCare",
    #             'SourceVersion': "Unknown",
    #             'EventName': event_name,
    #             'EventSubject': event_subject,
    #             'EventCategory': event_category,
    #             'ActionType': "User-Action",
    #             'ActionStatement': "User started careplan activity.",
    #             'Attributes': str(attributes),
    #             'Timestamp': careplan_task['StartedAt'],
    #             'UserRegistrationDate': careplan_task['UserRegistrationDate']
    #         }
    #         new_event_added = DataSynchronizer.add_event(careplan_task)
    #         if not new_event_added:
    #             print(f"Not inserted data.")
    #             return None
    #         else:
    #             return new_event_added
    #     except mysql.connector.Error as error:
    #         print(f"Failed to insert records: {error}")
    #         return None

    # @staticmethod
    # def sync_careplan_task_start_events(filters: DataSyncSearchFilter):
    #     try:
    #         existing_event_count = 0
    #         synched_event_count = 0
    #         event_not_synched = []
    #         careplan_tasks = CareplanEventsSynchronizer.get_reancare_careplan_task_start_events(filters)
    #         if careplan_tasks:
    #             for careplan_task in careplan_tasks:
    #                 existing_event = DataSynchronizer.get_existing_event(
    #                     careplan_task['UserId'], careplan_task['id'], EventType.CareplanTaskStart)
    #                 if existing_event is not None:
    #                     existing_event_count += 1
    #                 else:
    #                     new_event = CareplanEventsSynchronizer.add_analytics_careplan_task_start_event(careplan_task)
    #                     if new_event:
    #                         synched_event_count += 1
    #                     else:
    #                         event_not_synched.append(careplan_task)
    #             print(f"Existing Event Count: {existing_event_count}")
    #             print(f"Synched Event Count: {synched_event_count}")
    #             print(f"Event Not Synched: {event_not_synched}")
    #         else:
    #             print(f"No User Careplan Task Start Events found.")
    #     except Exception as error:
    #         print(f"Error syncing User Careplan Task Start Events: {error}")

    #endregion

    #region Careplan Task Complete events

    # @staticmethod
    # def get_reancare_careplan_task_complete_events(filters: DataSyncSearchFilter):
    #     try:
    #         selection_condition = f"AND user_task.FinishedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
    #         rean_db_connector = get_reancare_db_connector()
    #         query = f"""
    #         select 
    #             careplan_activity.id,
    #             careplan_activity.PatientUserId as UserId,
    #             careplan_activity.UserTaskId,
    #             careplan_activity.ProviderActionId,
    #             careplan_activity.EnrollmentId,
    #             careplan_activity.Provider,
    #             careplan_activity.PlanName,
    #             careplan_activity.PlanCode,
    #             careplan_activity.Type,
    #             careplan_activity.Category,
    #             careplan_activity.Title,
    #             careplan_activity.Description,
    #             careplan_activity.Transcription,
    #             careplan_activity.Url,
    #             careplan_activity.Language,
    #             careplan_activity.ScheduledAt,
    #             user_task.StartedAt,
    #             user_task.FinishedAt,
    #             careplan_activity.Sequence,
    #             careplan_activity.Frequency,
    #             careplan_activity.Status, 
    #             careplan_activity.UserResponse,
    #             careplan_activity.RawContent,
    #             careplan_activity.CreatedAt,
    #             careplan_activity.UpdatedAt,
    #             careplan_activity.DeletedAt,
    #             user.id as UserId,
    #             user.TenantId as TenantId,
    #             user.CreatedAt as UserRegistrationDate
    #         FROM careplan_activities AS careplan_activity
    #         JOIN user_tasks as user_task ON user_task.ActionId = careplan_activity.id
    #         JOIN users as user ON careplan_activity.PatientUserId = user.id
    #         WHERE
    #             user.IsTestUser = 0
    #             AND
    #             user_task.FinishedAt IS NOT null
    #             {selection_condition}
    #         """
    #         rows = rean_db_connector.execute_read_query(query)
    #         return rows
    #     except Exception as error:
    #         print("Error retrieving User Careplan Task Complete Events:", error)
    #         return None

    # @staticmethod
    # def add_analytics_careplan_task_complete_event(careplan_task):
    #     try:
    #         event_name = EventType.CareplanTaskComplete.value
    #         event_category = EventCategory.CareplanTask.value
    #         event_subject = EventSubject.CareplanTask.value
    #         # user = DataSynchronizer.get_user(medication['UserId'])
    #         # if not user:
    #         #     print(f"User not found for the event: {medication}")
    #         #     return None
    #         attributes = {
    #             'UserTaskId': careplan_task['UserTaskId'],
    #             'ProviderActionId': careplan_task['ProviderActionId'],
    #             'EnrollmentId': careplan_task['EnrollmentId'],
    #             'Provider': careplan_task['Provider'],
    #             'PlanName': careplan_task['PlanName'],
    #             'PlanCode': careplan_task['PlanCode'],
    #             'Type': careplan_task['Type'],
    #             'Category': careplan_task['Category'],
    #              'Title': careplan_task['Title'],
    #             'Description': careplan_task['Description'],
    #             'Transcription': careplan_task['Transcription'],
    #             'Url': careplan_task['Url'],
    #             'Language': careplan_task['Language'],
    #             'ScheduledAt': careplan_task['ScheduledAt'],
    #             'StartedAt': careplan_task['StartedAt'],
    #             'FinishedAt': careplan_task['FinishedAt'],
    #             'Sequence': careplan_task['Sequence'],
    #             'Frequency': careplan_task['Frequency'],
    #             'Status': careplan_task['Status'],
    #             'UserResponse': careplan_task['UserResponse'],
    #             'RawContent': careplan_task['RawContent'],
    #         }
    #         careplan_task = {
    #             'UserId': careplan_task['UserId'],
    #             'TenantId': careplan_task['TenantId'],
    #             'SessionId': None,
    #             'ResourceId': careplan_task['id'],
    #             'ResourceType': "Careplan-Task",
    #             'SourceName': "ReanCare",
    #             'SourceVersion': "Unknown",
    #             'EventName': event_name,
    #             'EventSubject': event_subject,
    #             'EventCategory': event_category,
    #             'ActionType': "User-Action",
    #             'ActionStatement': "User completed careplan activity.",
    #             'Attributes': str(attributes),
    #             'Timestamp': careplan_task['FinishedAt'],
    #             'UserRegistrationDate': careplan_task['UserRegistrationDate']
    #         }
    #         new_event_added = DataSynchronizer.add_event(careplan_task)
    #         if not new_event_added:
    #             print(f"Not inserted data.")
    #             return None
    #         else:
    #             return new_event_added
    #     except mysql.connector.Error as error:
    #         print(f"Failed to insert records: {error}")
    #         return None

    # @staticmethod
    # def sync_careplan_task_complete_events(filters: DataSyncSearchFilter):
    #     try:
    #         existing_event_count = 0
    #         synched_event_count = 0
    #         event_not_synched = []
    #         careplan_tasks = CareplanEventsSynchronizer.get_reancare_careplan_task_complete_events(filters)
    #         if careplan_tasks:
    #             for careplan_task in careplan_tasks:
    #                 existing_event = DataSynchronizer.get_existing_event(
    #                     careplan_task['UserId'], careplan_task['id'], EventType.CareplanTaskComplete)
    #                 if existing_event is not None:
    #                     existing_event_count += 1
    #                 else:
    #                     new_event = CareplanEventsSynchronizer.add_analytics_careplan_task_complete_event(careplan_task)
    #                     if new_event:
    #                         synched_event_count += 1
    #                     else:
    #                         event_not_synched.append(careplan_task)
    #             print(f"Existing Event Count: {existing_event_count}")
    #             print(f"Synched Event Count: {synched_event_count}")
    #             print(f"Event Not Synched: {event_not_synched}")
    #         else:
    #             print(f"No User Careplan Task Complete Events found.")
    #     except Exception as error:
    #         print(f"Error syncing User Careplan Task Complete Events: {error}")

    #endregion

    #region Careplan Task Cancelled events

    # @staticmethod
    # def get_reancare_careplan_task_cancel_events(filters: DataSyncSearchFilter):
    #     try:
    #         selection_condition = f"AND user_task.CancelledAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
    #         rean_db_connector = get_reancare_db_connector()
    #         query = f"""
    #         select 
    #             careplan_activity.id,
    #             careplan_activity.PatientUserId as UserId,
    #             careplan_activity.UserTaskId,
    #             careplan_activity.ProviderActionId,
    #             careplan_activity.EnrollmentId,
    #             careplan_activity.Provider,
    #             careplan_activity.PlanName,
    #             careplan_activity.PlanCode,
    #             careplan_activity.Type,
    #             careplan_activity.Category,
    #             careplan_activity.Title,
    #             careplan_activity.Description,
    #             careplan_activity.Transcription,
    #             careplan_activity.Url,
    #             careplan_activity.Language,
    #             careplan_activity.ScheduledAt,
    #             user_task.StartedAt,
    #             user_task.FinishedAt,
    #             user_task.CancelledAt,
    #             careplan_activity.Sequence,
    #             careplan_activity.Frequency,
    #             careplan_activity.Status, 
    #             careplan_activity.UserResponse,
    #             careplan_activity.RawContent,
    #             careplan_activity.CreatedAt,
    #             careplan_activity.UpdatedAt,
    #             careplan_activity.DeletedAt,
    #             user.id as UserId,
    #             user.TenantId as TenantId,
    #             user.CreatedAt as UserRegistrationDate
    #         FROM careplan_activities AS careplan_activity
    #         JOIN user_tasks as user_task ON user_task.ActionId = careplan_activity.id
    #         JOIN users as user ON careplan_activity.PatientUserId = user.id
    #         WHERE
    #             user.IsTestUser = 0
    #             AND
    #             user_task.CancelledAt IS NOT null
    #             {selection_condition}
    #         """
    #         rows = rean_db_connector.execute_read_query(query)
    #         return rows
    #     except Exception as error:
    #         print("Error retrieving User Careplan Task Cancel Events:", error)
    #         return None

    # @staticmethod
    # def add_analytics_careplan_task_cancel_event(careplan_task):
    #     try:
    #         event_name = EventType.CareplanStop.value
    #         event_category = EventCategory.Careplan.value
    #         event_subject = EventSubject.CareplanEnrollment.value
    #         # user = DataSynchronizer.get_user(medication['UserId'])
    #         # if not user:
    #         #     print(f"User not found for the event: {medication}")
    #         #     return None
    #         attributes = {
    #             'UserTaskId': careplan_task['UserTaskId'],
    #             'ProviderActionId': careplan_task['ProviderActionId'],
    #             'EnrollmentId': careplan_task['EnrollmentId'],
    #             'Provider': careplan_task['Provider'],
    #             'PlanName': careplan_task['PlanName'],
    #             'PlanCode': careplan_task['PlanCode'],
    #             'Type': careplan_task['Type'],
    #             'Category': careplan_task['Category'],
    #              'Title': careplan_task['Title'],
    #             'Description': careplan_task['Description'],
    #             'Transcription': careplan_task['Transcription'],
    #             'Url': careplan_task['Url'],
    #             'Language': careplan_task['Language'],
    #             'ScheduledAt': careplan_task['ScheduledAt'],
    #             'StartedAt': careplan_task['StartedAt'],
    #             'FinishedAt': careplan_task['FinishedAt'],
    #             'CancelledAt': careplan_task['CancelledAt'],
    #             'Sequence': careplan_task['Sequence'],
    #             'Frequency': careplan_task['Frequency'],
    #             'Status': careplan_task['Status'],
    #             'UserResponse': careplan_task['UserResponse'],
    #             'RawContent': careplan_task['RawContent'],
    #         }
    #         careplan_task = {
    #             'UserId': careplan_task['UserId'],
    #             'TenantId': careplan_task['TenantId'],
    #             'SessionId': None,
    #             'ResourceId': careplan_task['id'],
    #             'ResourceType': "careplan-enrollment",
    #             'SourceName': "ReanCare",
    #             'SourceVersion': "Unknown",
    #             'EventName': event_name,
    #             'EventSubject': event_subject,
    #             'EventCategory': event_category,
    #             'ActionType': "User-Action",
    #             'ActionStatement': "User cancel careplan activity.",
    #             'Attributes': str(attributes),
    #             'Timestamp': careplan_task['CancelledAt'],
    #             'UserRegistrationDate': careplan_task['UserRegistrationDate']
    #         }
    #         new_event_added = DataSynchronizer.add_event(careplan_task)
    #         if not new_event_added:
    #             print(f"Not inserted data.")
    #             return None
    #         else:
    #             return new_event_added
    #     except mysql.connector.Error as error:
    #         print(f"Failed to insert records: {error}")
    #         return None

    # @staticmethod
    # def sync_careplan_task_cancel_events(filters: DataSyncSearchFilter):
    #     try:
    #         existing_event_count = 0
    #         synched_event_count = 0
    #         event_not_synched = []
    #         careplan_tasks = CareplanEventsSynchronizer.get_reancare_careplan_task_cancel_events(filters)
    #         if careplan_tasks:
    #             for careplan_task in careplan_tasks:
    #                 existing_event = DataSynchronizer.get_existing_event(
    #                     careplan_task['UserId'], careplan_task['id'], EventType.CareplanTaskCancel)
    #                 if existing_event is not None:
    #                     existing_event_count += 1
    #                 else:
    #                     new_event = CareplanEventsSynchronizer.add_analytics_careplan_task_cancel_event(careplan_task)
    #                     if new_event:
    #                         synched_event_count += 1
    #                     else:
    #                         event_not_synched.append(careplan_task)
    #             print(f"Existing Event Count: {existing_event_count}")
    #             print(f"Synched Event Count: {synched_event_count}")
    #             print(f"Event Not Synched: {event_not_synched}")
    #         else:
    #             print(f"No User Careplan Task Cancel Events found.")
    #     except Exception as error:
    #         print(f"Error syncing User Careplan Task Cancel Events: {error}")

    #endregion

    @staticmethod
    def get_reancare_careplan_stop_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND careplanEnrollment.DeletedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                careplanEnrollment.id,
                careplanEnrollment.PatientUserId as UserId,
                careplanEnrollment.EnrollmentId,
                careplanEnrollment.ParticipantId,
                careplanEnrollment.Provider,
                careplanEnrollment.PlanCode,
                careplanEnrollment.PlanName,
                careplanEnrollment.StartDate,
                careplanEnrollment.EndDate,
                careplanEnrollment.IsActive,
                careplanEnrollment.Name,
                careplanEnrollment.HasHighRisk,
                careplanEnrollment.Complication,
                careplanEnrollment.ParticipantStringId,
                careplanEnrollment.EnrollmentStringId,
                careplanEnrollment.CreatedAt,
                careplanEnrollment.UpdatedAt,
                careplanEnrollment.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from careplan_enrollments as careplanEnrollment
            JOIN users as user ON careplanEnrollment.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                careplanEnrollment.DeletedAt IS NOT null;
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Careplan Stop Events:", error)
            return None

    @staticmethod
    def add_analytics_careplan_stop_event(careplan_task):
        try:
            event_name = EventType.CareplanStop.value
            event_category = EventCategory.Careplan.value
            event_subject = EventSubject.CareplanEnrollment.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'PatientUserId' : careplan_task['UserId'],
                'Provider'      : careplan_task['Provider'],
                'PlanName'      : careplan_task['PlanName'],
                'PlanCode'      : careplan_task['PlanCode'],
                'StartDate'     : careplan_task['StartedAt'],
                'EndDate'       : careplan_task['EndDate'],
                'StoppedAt'     : careplan_task['DeletedAt']
                # 'UserTaskId': careplan_task['UserTaskId'],
                # 'ProviderActionId': careplan_task['ProviderActionId'],
                # 'EnrollmentId': careplan_task['EnrollmentId'],
                # 'Provider': careplan_task['Provider'],
                # 'PlanName': careplan_task['PlanName'],
                # 'PlanCode': careplan_task['PlanCode'],
                # 'Type': careplan_task['Type'],
                # 'Category': careplan_task['Category'],
                #  'Title': careplan_task['Title'],
                # 'Description': careplan_task['Description'],
                # 'Transcription': careplan_task['Transcription'],
                # 'Url': careplan_task['Url'],
                # 'Language': careplan_task['Language'],
                # 'ScheduledAt': careplan_task['ScheduledAt'],
                # 'StartedAt': careplan_task['StartedAt'],
                # 'FinishedAt': careplan_task['FinishedAt'],
                # 'CancelledAt': careplan_task['CancelledAt'],
                # 'Sequence': careplan_task['Sequence'],
                # 'Frequency': careplan_task['Frequency'],
                # 'Status': careplan_task['Status'],
                # 'UserResponse': careplan_task['UserResponse'],
                # 'RawContent': careplan_task['RawContent'],
            }
            careplan_task = {
                'UserId': careplan_task['UserId'],
                'TenantId': careplan_task['TenantId'],
                'SessionId': None,
                'ResourceId': careplan_task['id'],
                'ResourceType': "careplan-enrollment",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User cancel careplan activity.",
                'Attributes': str(attributes),
                'Timestamp': careplan_task['CancelledAt'],
                'UserRegistrationDate': careplan_task['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(careplan_task)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None
        
    @staticmethod
    def sync_careplan_stop_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            careplan_tasks = CareplanEventsSynchronizer.get_reancare_careplan_stop_events(filters)
            if careplan_tasks:
                for careplan_task in careplan_tasks:
                    existing_event = DataSynchronizer.get_existing_event(
                        careplan_task['UserId'], careplan_task['id'], EventType.CareplanStop)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = CareplanEventsSynchronizer.add_analytics_careplan_stop_event(careplan_task)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(careplan_task)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Careplan Stop Events found.")
        except Exception as error:
            print(f"Error syncing User Careplan Stop Events: {error}")

