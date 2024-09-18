from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class AssessmentEventsSynchronizer:

    #region Create Assessment events

    @staticmethod
    def get_reancare_assessment_create_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND assessment.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                assessment.id,
                assessment.PatientUserId as UserId,
                assessment.DisplayCode,
                assessment.Title,
                assessment.Description,
                assessment.AssessmentTemplateId,
                assessment.ScoringApplicable,
                assessment.Type,
                assessment.Provider,
                assessment.ProviderAssessmentCode,
                assessment.ProviderAssessmentId,
                assessment.ProviderEnrollmentId,
                assessment.ReportUrl,
                assessment.Status,
                assessment.StartedAt,
                assessment.FinishedAt,
                assessment.ScheduledDateString,
                assessment.CurrentNodeId,
                assessment.ParentActivityId,
                assessment.UserTaskId,
                assessment.ScoreDetails,
                assessment.TotalNumberOfQuestions,
                assessment.CreatedAt,
                assessment.UpdatedAt,
                assessment.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from assessments as assessment
            JOIN users as user ON assessment.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Assessment Create Events:", error)
            return None

    @staticmethod
    def add_analytics_assessment_create_event(assessment):
        try:
            event_name = EventType.AssessmentCreate.value
            event_category = EventCategory.Assessment.value
            event_subject = EventSubject.Assessment.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'DisplayCode': assessment['DisplayCode'],
                'Title': assessment['Title'],
                'Description': assessment['Description'],
                'AssessmentTemplateId': assessment['AssessmentTemplateId'],
                'ScoringApplicable': assessment['ScoringApplicable'],
                'Type': assessment['Type'],
                'Provider': assessment['Provider'],
                'ProviderAssessmentCode': assessment['ProviderAssessmentCode'],
                'ProviderAssessmentId': assessment['ProviderAssessmentId'],
                'ProviderEnrollmentId': assessment['ProviderEnrollmentId'],
                'ReportUrl': assessment['ReportUrl'],
                'Status': assessment['Status'],
                'StartedAt': assessment['StartedAt'],
                'FinishedAt': assessment['FinishedAt'],
                'ScheduledDateString': assessment['ScheduledDateString'],
                'CurrentNodeId': assessment['CurrentNodeId'],
                'ParentActivityId': assessment['ParentActivityId'],
                'UserTaskId': assessment['UserTaskId'],
                'ScoreDetails': assessment['ScoreDetails'],
                'TotalNumberOfQuestions': assessment['TotalNumberOfQuestions'],
            }
            assessment = {
                'UserId': assessment['UserId'],
                'TenantId': assessment['TenantId'],
                'SessionId': None,
                'ResourceId': assessment['id'],
                'ResourceType': "assessment",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "Assessment is created for user.",
                'Attributes': str(attributes),
                'Timestamp': assessment['CreatedAt'],
                'UserRegistrationDate': assessment['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(assessment)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_assessment_create_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            assessments = AssessmentEventsSynchronizer.get_reancare_assessment_create_events(filters)
            if assessments:
                for assessment in assessments:
                    existing_event = DataSynchronizer.get_existing_event(
                        assessment['UserId'], assessment['id'], EventType.AssessmentCreate)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = AssessmentEventsSynchronizer.add_analytics_assessment_create_event(assessment)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(assessments)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Assessment Create Events found.")
        except Exception as error:
            print(f"Error syncing User Assessment Create Events: {error}")

    #endregion

    #region Create Assessment Delete events

    @staticmethod
    def get_reancare_assessment_delete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND assessment.DeletedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                assessment.id,
                assessment.PatientUserId as UserId,
                assessment.DisplayCode,
                assessment.Title,
                assessment.Description,
                assessment.AssessmentTemplateId,
                assessment.ScoringApplicable,
                assessment.Type,
                assessment.Provider,
                assessment.ProviderAssessmentCode,
                assessment.ProviderAssessmentId,
                assessment.ProviderEnrollmentId,
                assessment.ReportUrl,
                assessment.Status,
                assessment.StartedAt,
                assessment.FinishedAt,
                assessment.ScheduledDateString,
                assessment.CurrentNodeId,
                assessment.ParentActivityId,
                assessment.UserTaskId,
                assessment.ScoreDetails,
                assessment.TotalNumberOfQuestions,
                assessment.CreatedAt,
                assessment.UpdatedAt,
                assessment.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from assessments as assessment
            JOIN users as user ON assessment.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                assessment.DeletedAt IS NOT NULL
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Assessment Delete Events:", error)
            return None

    @staticmethod
    def add_analytics_assessment_delete_event(assessment):
        try:
            event_name = EventType.AssessmentDelete.value
            event_category = EventCategory.Assessment.value
            event_subject = EventSubject.Assessment.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'DisplayCode': assessment['DisplayCode'],
                'Title': assessment['Title'],
                'Description': assessment['Description'],
                'AssessmentTemplateId': assessment['AssessmentTemplateId'],
                'ScoringApplicable': assessment['ScoringApplicable'],
                'Type': assessment['Type'],
                'Provider': assessment['Provider'],
                'ProviderAssessmentCode': assessment['ProviderAssessmentCode'],
                'ProviderAssessmentId': assessment['ProviderAssessmentId'],
                'ProviderEnrollmentId': assessment['ProviderEnrollmentId'],
                'ReportUrl': assessment['ReportUrl'],
                'Status': assessment['Status'],
                'StartedAt': assessment['StartedAt'],
                'FinishedAt': assessment['FinishedAt'],
                'ScheduledDateString': assessment['ScheduledDateString'],
                'CurrentNodeId': assessment['CurrentNodeId'],
                'ParentActivityId': assessment['ParentActivityId'],
                'UserTaskId': assessment['UserTaskId'],
                'ScoreDetails': assessment['ScoreDetails'],
                'TotalNumberOfQuestions': assessment['TotalNumberOfQuestions'],
            }
            assessment = {
                'UserId': assessment['UserId'],
                'TenantId': assessment['TenantId'],
                'SessionId': None,
                'ResourceId': assessment['id'],
                'ResourceType': "assessment",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "Assessment is deleted.",
                'Attributes': str(attributes),
                'Timestamp': assessment['DeletedAt'],
                'UserRegistrationDate': assessment['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(assessment)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_assessment_delete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            assessments = AssessmentEventsSynchronizer.get_reancare_assessment_delete_events(filters)
            if assessments:
                for assessment in assessments:
                    existing_event = DataSynchronizer.get_existing_event(
                        assessment['UserId'], assessment['id'], EventType.AssessmentDelete)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = AssessmentEventsSynchronizer.add_analytics_assessment_delete_event(assessment)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(assessments)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Assessment Delete Events found.")
        except Exception as error:
            print(f"Error syncing User Assessment Delete Events: {error}")

    #endregion

    #region Start Assessment events

    @staticmethod
    def get_reancare_assessment_start_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND assessment.StartedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                assessment.id,
                assessment.PatientUserId as UserId,
                assessment.DisplayCode,
                assessment.Title,
                assessment.Description,
                assessment.AssessmentTemplateId,
                assessment.ScoringApplicable,
                assessment.Type,
                assessment.Provider,
                assessment.ProviderAssessmentCode,
                assessment.ProviderAssessmentId,
                assessment.ProviderEnrollmentId,
                assessment.ReportUrl,
                assessment.Status,
                assessment.StartedAt,
                assessment.FinishedAt,
                assessment.ScheduledDateString,
                assessment.CurrentNodeId,
                assessment.ParentActivityId,
                assessment.UserTaskId,
                assessment.ScoreDetails,
                assessment.TotalNumberOfQuestions,
                assessment.CreatedAt,
                assessment.UpdatedAt,
                assessment.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from assessments as assessment
            JOIN users as user ON assessment.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                assessment.StartedAt IS NOT null
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Assessment start Events:", error)
            return None

    @staticmethod
    def add_analytics_assessment_start_event(assessment):
        try:
            event_name = EventType.AssessmentStart.value
            event_category = EventCategory.Assessment.value
            event_subject = EventSubject.Assessment.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'DisplayCode': assessment['DisplayCode'],
                'Title': assessment['Title'],
                'Description': assessment['Description'],
                'AssessmentTemplateId': assessment['AssessmentTemplateId'],
                'ScoringApplicable': assessment['ScoringApplicable'],
                'Type': assessment['Type'],
                'Provider': assessment['Provider'],
                'ProviderAssessmentCode': assessment['ProviderAssessmentCode'],
                'ProviderAssessmentId': assessment['ProviderAssessmentId'],
                'ProviderEnrollmentId': assessment['ProviderEnrollmentId'],
                'ReportUrl': assessment['ReportUrl'],
                'Status': assessment['Status'],
                'StartedAt': assessment['StartedAt'],
                'FinishedAt': assessment['FinishedAt'],
                'ScheduledDateString': assessment['ScheduledDateString'],
                'CurrentNodeId': assessment['CurrentNodeId'],
                'ParentActivityId': assessment['ParentActivityId'],
                'UserTaskId': assessment['UserTaskId'],
                'ScoreDetails': assessment['ScoreDetails'],
                'TotalNumberOfQuestions': assessment['TotalNumberOfQuestions'],
            }
            assessment = {
                'UserId': assessment['UserId'],
                'TenantId': assessment['TenantId'],
                'SessionId': None,
                'ResourceId': assessment['id'],
                'ResourceType': "assessment",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User started the assessment.",
                'Attributes': str(attributes),
                'Timestamp': assessment['StartedAt'],
                'UserRegistrationDate': assessment['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(assessment)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_assessment_start_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            assessments = AssessmentEventsSynchronizer.get_reancare_assessment_start_events(filters)
            if assessments:
                for assessment in assessments:
                    existing_event = DataSynchronizer.get_existing_event(
                        assessment['UserId'], assessment['id'], EventType.AssessmentStart)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = AssessmentEventsSynchronizer.add_analytics_assessment_start_event(assessment)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(assessment)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Assessment start Events found.")
        except Exception as error:
            print(f"Error syncing User Assessment Start Events: {error}")

    #endregion
    
    #region Complete Assessment events

    @staticmethod
    def get_reancare_assessment_complete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND assessment.FinishedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                assessment.id,
                assessment.PatientUserId as UserId,
                assessment.DisplayCode,
                assessment.Title,
                assessment.Description,
                assessment.AssessmentTemplateId,
                assessment.ScoringApplicable,
                assessment.Type,
                assessment.Provider,
                assessment.ProviderAssessmentCode,
                assessment.ProviderAssessmentId,
                assessment.ProviderEnrollmentId,
                assessment.ReportUrl,
                assessment.Status,
                assessment.StartedAt,
                assessment.FinishedAt,
                assessment.ScheduledDateString,
                assessment.CurrentNodeId,
                assessment.ParentActivityId,
                assessment.UserTaskId,
                assessment.ScoreDetails,
                assessment.TotalNumberOfQuestions,
                assessment.CreatedAt,
                assessment.UpdatedAt,
                assessment.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from assessments as assessment
            JOIN users as user ON assessment.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                assessment.FinishedAt IS NOT null
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Assessment Complete Events:", error)
            return None

    @staticmethod
    def add_analytics_assessment_complete_event(assessment):
        try:
            event_name = EventType.AssessmentComplete.value
            event_category = EventCategory.Assessment.value
            event_subject = EventSubject.Assessment.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'DisplayCode': assessment['DisplayCode'],
                'Title': assessment['Title'],
                'Description': assessment['Description'],
                'AssessmentTemplateId': assessment['AssessmentTemplateId'],
                'ScoringApplicable': assessment['ScoringApplicable'],
                'Type': assessment['Type'],
                'Provider': assessment['Provider'],
                'ProviderAssessmentCode': assessment['ProviderAssessmentCode'],
                'ProviderAssessmentId': assessment['ProviderAssessmentId'],
                'ProviderEnrollmentId': assessment['ProviderEnrollmentId'],
                'ReportUrl': assessment['ReportUrl'],
                'Status': assessment['Status'],
                'StartedAt': assessment['StartedAt'],
                'FinishedAt': assessment['FinishedAt'],
                'ScheduledDateString': assessment['ScheduledDateString'],
                'CurrentNodeId': assessment['CurrentNodeId'],
                'ParentActivityId': assessment['ParentActivityId'],
                'UserTaskId': assessment['UserTaskId'],
                'ScoreDetails': assessment['ScoreDetails'],
                'TotalNumberOfQuestions': assessment['TotalNumberOfQuestions'],
            }
            assessment = {
                'UserId': assessment['UserId'],
                'TenantId': assessment['TenantId'],
                'SessionId': None,
                'ResourceId': assessment['id'],
                'ResourceType': "assessment",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User started the assessment.",
                'Attributes': str(attributes),
                'Timestamp': assessment['FinishedAt'],
                'UserRegistrationDate': assessment['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(assessment)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_assessment_complete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            assessments = AssessmentEventsSynchronizer.get_reancare_assessment_complete_events(filters)
            if assessments:
                for assessment in assessments:
                    existing_event = DataSynchronizer.get_existing_event(
                        assessment['UserId'], assessment['id'], EventType.AssessmentComplete)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = AssessmentEventsSynchronizer.add_analytics_assessment_complete_event(assessment)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(assessment)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Assessment Complete Events found.")
        except Exception as error:
            print(f"Error syncing User Assessment Complete Events: {error}")

    #endregion

     #region Assessment Question Answered events

    @staticmethod
    def get_reancare_assessment_question_answered_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND assessmentQueryResponse.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT 
                assessmentQueryResponse.id,
                assessment.PatientUserId as UserId,
                assessmentQueryResponse.AssessmentId,
                assessmentQueryResponse.NodeId,
                assessmentQueryResponse.Type,
                assessmentQueryResponse.Sequence,
                assessmentQueryResponse.IntegerValue,
                assessmentQueryResponse.FloatValue,
                assessmentQueryResponse.BooleanValue,
                assessmentQueryResponse.DateValue,
                assessmentQueryResponse.Url,
                assessmentQueryResponse.ResourceId,
                assessmentQueryResponse.TextValue,
                assessmentQueryResponse.Additional,
                assessmentQueryResponse.CreatedAt,
                assessmentQueryResponse.UpdatedAt,
                assessmentQueryResponse.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            FROM assessment_query_responses as assessmentQueryResponse
            JOIN assessments as assessment ON assessmentQueryResponse.AssessmentId = assessment.id
            JOIN users as user ON user.id = assessment.PatientUserId
            WHERE 
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Assessment Question Answered Events:", error)
            return None

    @staticmethod
    def add_analytics_assessment_question_answered_event(assessment):
        try:
            event_name = EventType.AssessmentQuestionAnswer.value
            event_category = EventCategory.Assessment.value
            event_subject = EventSubject.AssessmentQuestion.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'AssessmentId': assessment['AssessmentId'],
                'NodeId': assessment['NodeId'],
                'Type': assessment['Type'],
                'Sequence': assessment['Sequence'],
                'IntegerValue': assessment['IntegerValue'],
                'FloatValue': assessment['FloatValue'],
                'BooleanValue': assessment['BooleanValue'],
                'DateValue': assessment['DateValue'],
                'Url': assessment['Url'],
                'ResourceId': assessment['ResourceId'],
                'TextValue': assessment['TextValue'],
                'Additional': assessment['Additional'],
            }
            assessment = {
                'UserId': assessment['UserId'],
                'TenantId': assessment['TenantId'],
                'SessionId': None,
                'ResourceId': assessment['id'],
                'ResourceType': "assessment",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User answered a question.",
                'Attributes': str(attributes),
                'Timestamp': assessment['CreatedAt'],
                'UserRegistrationDate': assessment['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(assessment)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_assessment_question_answered_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            assessments = AssessmentEventsSynchronizer.get_reancare_assessment_question_answered_events(filters)
            if assessments:
                for assessment in assessments:
                    existing_event = DataSynchronizer.get_existing_event(
                        assessment['UserId'], assessment['id'], EventType.AssessmentQuestionAnswer)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = AssessmentEventsSynchronizer.add_analytics_assessment_question_answered_event(assessment)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(assessment)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Assessment Question Answered Events found.")
        except Exception as error:
            print(f"Error syncing User Assessment Question Answered Events: {error}")

    #endregion
