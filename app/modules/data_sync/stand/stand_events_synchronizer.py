from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class StandEventsSynchronizer:

    #region Add Symptom events

    @staticmethod
    def get_reancare_stand_create_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND stand.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                stand.id,
                stand.PersonId,
                stand.PatientUserId as UserId,
                stand.Stand,
                stand.Unit,
                stand.RecordDate,
                stand.CreatedAt,
                stand.UpdatedAt,
                stand.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from daily_records_stand as stand
            JOIN users as user ON stand.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Stand Create Events:", error)
            return None

    @staticmethod
    def add_analytics_stand_create_event(stand):
        try:
            event_name = EventType.StandRecordAdd.value
            event_category = EventCategory.Stand.value
            event_subject = EventSubject.Stand.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'PersonId': stand['PersonId'],
                'PatientUserId': stand['UserId'],
                'Stand': stand['Stand'],
                'Unit': stand['Unit'], 
                'RecordDate': stand['RecordDate']           
             }
            stand = {
                'UserId': stand['UserId'],
                'TenantId': stand['TenantId'],
                'SessionId': None,
                'ResourceId': stand['id'],
                'ResourceType': "stand",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User added a stand.",
                'Attributes': str(attributes),
                'Timestamp': stand['CreatedAt'],
                'UserRegistrationDate': stand['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(stand)
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
    def sync_stand_create_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            stands = StandEventsSynchronizer.get_reancare_stand_create_events(filters)
            if stands:
                for stand in stands:
                    existing_event = DataSynchronizer.get_existing_event(
                        stand['UserId'], stand['id'], EventType.StandRecordAdd)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = StandEventsSynchronizer.add_analytics_stand_create_event(stand)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(stand)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Stand Create Events found.")
        except Exception as error:
            print(f"Error syncing User Stand Create Events: {error}")
    
    #endregion
