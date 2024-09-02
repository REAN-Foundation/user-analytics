from app.domain_types.enums.event_types import EventType
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class MedicationEventsSynchronizer:

    @staticmethod
    def get_reancare_user_medication_create_events():
        try:
            rean_db_connector = DataSynchronizer.get_reancare_db_connector()
            query = f"""
            SELECT * from user_medication_create_events
            WHERE
                DeletedAt IS NULL
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Medication Create Events:", error)
            return None

    @staticmethod
    def add_medication_create_event(event, user):
        try:
            event_name = EventType.UserMedicationCreate.value
            event = {
                'UserId': event['UserId'],
                'TenantId': user['TenantId'],
                'SessionId': event['id'],
                'ResourceId': event['id'],
                'ResourceType': "User-Medication-Create-Event",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventCategory': "User-Medication-Create-Event",
                'ActionType': "User-Action",
                'ActionStatement': "User created a medication.",
                'Attributes': "{}",
                'Timestamp': event['CreatedAt'],
                'RegistrationDate': user['CreatedAt']
            }
            new_event_added = DataSynchronizer.add_event(event)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                print(f"Inserted row into the user_medication_create_events table.")
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_user_medication_create_events():
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            rean_events = MedicationEventsSynchronizer.get_reancare_user_medication_create_events()
            if rean_events:
                for event in rean_events:
                    user = DataSynchronizer.get_user(event['UserId'])
                    if user:
                        existing_event_count += 1
                        new_event = MedicationEventsSynchronizer.add_medication_create_event(event, user)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(event)
                    else:
                        print(f"User not found for the event: {event}")
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Medication Create Events found.")
        except Exception as error:
            print(f"Error syncing User Medication Create Events: {error}")
