from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class SymptomEventsSynchronizer:

    #region Add Symptom events

    @staticmethod
    def get_reancare_symptom_create_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND symptom.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                symptom.id,
                symptom.PatientUserId as UserId,
                symptom.EhrId,
                symptom.MedicalPractitionerUserId,
                symptom.VisitId,
                symptom.AssessmentId,
                symptom.AssessmentTemplateId,
                symptom.SymptomTypeId,
                symptom.Symptom,
                symptom.IsPresent,
                symptom.Severity,
                symptom.ValidationStatus,
                symptom.Interpretation,
                symptom.Comments,
                symptom.RecordDate,
                symptom.CreatedAt,
                symptom.UpdatedAt,
                symptom.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from symptoms as symptom
            JOIN users as user ON symptom.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            print(query)
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Symptom Create Events:", error)
            return None

    @staticmethod
    def add_analytics_symptom_create_event(symptom):
        try:
            event_name = EventType.SymptomAdd.value
            event_category = EventCategory.Symptoms.value
            event_subject = symptom['Symptom']
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': symptom['EhrId'],
                'MedicalPractitionerUserId': symptom['MedicalPractitionerUserId'],
                'VisitId': symptom['VisitId'],
                'AssessmentId': symptom['AssessmentId'],
                'AssessmentTemplateId': symptom['AssessmentTemplateId'],
                'SymptomTypeId': symptom['SymptomTypeId'],
                'Symptom': symptom['Symptom'],
                'IsPresent': symptom['IsPresent'],
                'Severity': symptom['Severity'],
                'ValidationStatus': symptom['ValidationStatus'],
                'Interpretation': symptom['Interpretation'],
                'Comments': symptom['Comments'],
                'RecordDate': symptom['RecordDate'],
             }
            symptom = {
                'UserId': symptom['UserId'],
                'TenantId': symptom['TenantId'],
                'SessionId': None,
                'ResourceId': symptom['id'],
                'ResourceType': "symptom",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User added a symptom.",
                'Attributes': str(attributes),
                'Timestamp': symptom['CreatedAt'],
                'UserRegistrationDate': symptom['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(symptom)
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
    def sync_symptom_create_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            symptoms = SymptomEventsSynchronizer.get_reancare_symptom_create_events(filters)
            if symptoms:
                for symptom in symptoms:
                    existing_event = DataSynchronizer.get_existing_event(
                        symptom['UserId'], symptom['id'], EventType.SymptomAdd)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = SymptomEventsSynchronizer.add_analytics_symptom_create_event(symptom)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(symptom)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Symptom Create Events found.")
        except Exception as error:
            print(f"Error syncing User Symptom Create Events: {error}")

    #endregion

    #region Update Symptom events

    @staticmethod
    def get_reancare_symptom_update_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND symptom.UpdatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                symptom.id,
                symptom.PatientUserId as UserId,
                symptom.EhrId,
                symptom.MedicalPractitionerUserId,
                symptom.VisitId,
                symptom.AssessmentId,
                symptom.AssessmentTemplateId,
                symptom.SymptomTypeId,
                symptom.Symptom,
                symptom.IsPresent,
                symptom.Severity,
                symptom.ValidationStatus,
                symptom.Interpretation,
                symptom.Comments,
                symptom.RecordDate,
                symptom.CreatedAt,
                symptom.UpdatedAt,
                symptom.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from symptoms as symptom
            JOIN users as user ON symptom.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                symptom.CreatedAt <> symptom.UpdatedAt
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Symptom Update Events:", error)
            return None

    @staticmethod
    def add_analytics_symptom_update_event(symptom):
        try:
            event_name = EventType.SymptomUpdate.value
            event_category = EventCategory.Symptoms.value
            event_subject = symptom['Symptom']
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': symptom['EhrId'],
                'MedicalPractitionerUserId': symptom['MedicalPractitionerUserId'],
                'VisitId': symptom['VisitId'],
                'AssessmentId': symptom['AssessmentId'],
                'AssessmentTemplateId': symptom['AssessmentTemplateId'],
                'SymptomTypeId': symptom['SymptomTypeId'],
                'Symptom': symptom['Symptom'],
                'IsPresent': symptom['IsPresent'],
                'Severity': symptom['Severity'],
                'ValidationStatus': symptom['ValidationStatus'],
                'Interpretation': symptom['Interpretation'],
                'Comments': symptom['Comments'],
                'RecordDate': symptom['RecordDate'],
             }
            symptom = {
                'UserId': symptom['UserId'],
                'TenantId': symptom['TenantId'],
                'SessionId': None,
                'ResourceId': symptom['id'],
                'ResourceType': "symptom",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User updated a symptom.",
                'Attributes': str(attributes),
                'Timestamp': symptom['UpdatedAt'],
                'UserRegistrationDate': symptom['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(symptom)
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
    def sync_symptom_update_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            symptoms = SymptomEventsSynchronizer.get_reancare_symptom_update_events(filters)
            if symptoms:
                for symptom in symptoms:
                    existing_event = DataSynchronizer.get_existing_event(
                        symptom['UserId'], symptom['id'], EventType.SymptomUpdate)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = SymptomEventsSynchronizer.add_analytics_symptom_update_event(symptom)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(symptom)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Symptom Update Events found.")
        except Exception as error:
            print(f"Error syncing User Symptom Update Events: {error}")

    #endregion

    #region Update Symptom events

    @staticmethod
    def get_reancare_symptom_delete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND symptom.DeletedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                symptom.id,
                symptom.PatientUserId as UserId,
                symptom.EhrId,
                symptom.MedicalPractitionerUserId,
                symptom.VisitId,
                symptom.AssessmentId,
                symptom.AssessmentTemplateId,
                symptom.SymptomTypeId,
                symptom.Symptom,
                symptom.IsPresent,
                symptom.Severity,
                symptom.ValidationStatus,
                symptom.Interpretation,
                symptom.Comments,
                symptom.RecordDate,
                symptom.CreatedAt,
                symptom.UpdatedAt,
                symptom.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from symptoms as symptom
            JOIN users as user ON symptom.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                symptom.DeletedAt IS NOT null
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Symptom Delete Events:", error)
            return None

    @staticmethod
    def add_analytics_symptom_delete_event(symptom):
        try:
            event_name = EventType.SymptomDelete.value
            event_category = EventCategory.Symptoms.value
            event_subject = symptom['Symptom']
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': symptom['EhrId'],
                'MedicalPractitionerUserId': symptom['MedicalPractitionerUserId'],
                'VisitId': symptom['VisitId'],
                'AssessmentId': symptom['AssessmentId'],
                'AssessmentTemplateId': symptom['AssessmentTemplateId'],
                'SymptomTypeId': symptom['SymptomTypeId'],
                'Symptom': symptom['Symptom'],
                'IsPresent': symptom['IsPresent'],
                'Severity': symptom['Severity'],
                'ValidationStatus': symptom['ValidationStatus'],
                'Interpretation': symptom['Interpretation'],
                'Comments': symptom['Comments'],
                'RecordDate': symptom['RecordDate'],
             }
            symptom = {
                'UserId': symptom['UserId'],
                'TenantId': symptom['TenantId'],
                'SessionId': None,
                'ResourceId': symptom['id'],
                'ResourceType': "symptom",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User deleted a symptom.",
                'Attributes': str(attributes),
                'Timestamp': symptom['DeletedAt'],
                'UserRegistrationDate': symptom['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(symptom)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_symptom_delete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            symptoms = SymptomEventsSynchronizer.get_reancare_symptom_delete_events(filters)
            if symptoms:
                for symptom in symptoms:
                    existing_event = DataSynchronizer.get_existing_event(
                        symptom['UserId'], symptom['id'], EventType.SymptomDelete)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = SymptomEventsSynchronizer.add_analytics_symptom_delete_event(symptom)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(symptom)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Symptom Delete Events found.")
        except Exception as error:
            print(f"Error syncing User Symptom Delete Events: {error}")

    #endregion
