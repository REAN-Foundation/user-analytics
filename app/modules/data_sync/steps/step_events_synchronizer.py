from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class StepEventsSynchronizer:

    #region Add Symptom events

    @staticmethod
    def get_reancare_step_create_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND step.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                step.id,
                step.PersonId,
                step.PatientUserId as UserId,
                step.Provider,
                step.TerraSummaryId,
                step.StepCount,
                step.Unit,
                step.RecordDate,
                step.CreatedAt,
                step.UpdatedAt,
                step.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from daily_records_step_count as step
            JOIN users as user ON step.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            print(query)
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User step Create Events:", error)
            return None

    @staticmethod
    def add_analytics_step_create_event(step):
        try:
            event_name = EventType.StepRecordAdd.value
            event_category = EventCategory.Steps.value
            event_subject = EventSubject.Step.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'PersonId': step['PersonId'],
                'Provider': step['Provider'],
                'TerraSummaryId': step['TerraSummaryId'], 
                'StepCount': step['StepCount'],
                'Unit': step['Unit'], 
                'RecordDate': step['RecordDate']             
             }
            step = {
                'UserId': step['UserId'],
                'TenantId': step['TenantId'],
                'SessionId': None,
                'ResourceId': step['id'],
                'ResourceType': "step",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User added a step.",
                'Attributes': str(attributes),
                'Timestamp': step['CreatedAt'],
                'UserRegistrationDate': step['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(step)
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
    def sync_step_create_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            steps = StepEventsSynchronizer.get_reancare_step_create_events(filters)
            if steps:
                for step in steps:
                    existing_event = DataSynchronizer.get_existing_event(
                        step['UserId'], step['id'], EventType.StepRecordAdd)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = StepEventsSynchronizer.add_analytics_step_create_event(step)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(step)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Step Create Events found.")
        except Exception as error:
            print(f"Error syncing User Step Create Events: {error}")
    
    #endregion
