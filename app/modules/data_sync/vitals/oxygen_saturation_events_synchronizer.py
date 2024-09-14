from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class OxygenSaturationEventsSynchronizer:

    #region Create Blood Oxygen Saturation events

    @staticmethod
    def get_reancare_oxygen_saturation_create_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND oxygenSaturation.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                oxygenSaturation.id,
                oxygenSaturation.PatientUserId as UserId,
                oxygenSaturation.EhrId,
                oxygenSaturation.Provider,
                oxygenSaturation.TerraSummaryId,
                oxygenSaturation.BloodOxygenSaturation,
                oxygenSaturation.Unit,
                oxygenSaturation.RecordDate,
                oxygenSaturation.RecordedByUserId,
                oxygenSaturation.CreatedAt,
                oxygenSaturation.UpdatedAt,
                oxygenSaturation.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from biometrics_blood_oxygen_saturation as oxygenSaturation
            JOIN users as user ON oxygenSaturation.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Oxygen Saturation Create Events:", error)
            return None

    @staticmethod
    def add_analytics_oxygen_saturation_create_event(oxygen_saturation):
        try:
            event_name = EventType.VitalAddOxygenSaturation.value
            event_category = EventCategory.Vitals.value
            event_subject = EventSubject.Vital.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': oxygen_saturation['EhrId'],
                'Provider': oxygen_saturation['Provider'],
                'TerraSummaryId': oxygen_saturation['TerraSummaryId'],
                'BloodOxygenSaturation': oxygen_saturation['BloodOxygenSaturation'],
                'Unit': oxygen_saturation['Unit'],
                'RecordDate': oxygen_saturation['RecordDate'],
                'RecordedByUserId': oxygen_saturation['RecordedByUserId'],
            }
            oxygen_saturation = {
                'UserId': oxygen_saturation['UserId'],
                'TenantId': oxygen_saturation['TenantId'],
                'SessionId': None,
                'ResourceId': oxygen_saturation['id'],
                'ResourceType': "Biometric",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User added a blood oxygen saturation.",
                'Attributes': str(attributes),
                'Timestamp': oxygen_saturation['CreatedAt'],
                'UserRegistrationDate': oxygen_saturation['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(oxygen_saturation)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_oxygen_saturation_create_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            oxygen_saturation_records = OxygenSaturationEventsSynchronizer.get_reancare_oxygen_saturation_create_events(filters)
            if oxygen_saturation_records:
                for oxygen_saturation in oxygen_saturation_records:
                    existing_event = DataSynchronizer.get_existing_event(
                        oxygen_saturation['UserId'], oxygen_saturation['id'], EventType.VitalAddOxygenSaturation)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = OxygenSaturationEventsSynchronizer.add_analytics_oxygen_saturation_create_event(oxygen_saturation)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(oxygen_saturation)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Blood Oxygen Saturation Create Events found.")
        except Exception as error:
            print(f"Error syncing User Blood Oxygen Saturation Create Events: {error}")

    #endregion

    #region Delete Blood Oxygen Saturation events

    @staticmethod
    def get_reancare_oxygen_saturation_delete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND oxygenSaturation.DeletedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
             SELECT
                oxygenSaturation.id,
                oxygenSaturation.PatientUserId as UserId,
                oxygenSaturation.EhrId,
                oxygenSaturation.Provider,
                oxygenSaturation.TerraSummaryId,
                oxygenSaturation.BloodOxygenSaturation,
                oxygenSaturation.Unit,
                oxygenSaturation.RecordDate,
                oxygenSaturation.RecordedByUserId,
                oxygenSaturation.CreatedAt,
                oxygenSaturation.UpdatedAt,
                oxygenSaturation.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from biometrics_blood_oxygen_saturation as oxygenSaturation
            JOIN users as user ON oxygenSaturation.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                oxygenSaturation.DeletedAt IS NOT NULL
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Blood Oxygen Saturation Delete Events:", error)
            return None

    @staticmethod
    def add_analytics_oxygen_saturation_delete_event(oxygen_saturation):
        try:
            event_name = EventType.VitalDeleteOxygenSaturation.value
            event_category = EventCategory.Vitals.value
            event_subject = EventSubject.Vital.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
           'EhrId': oxygen_saturation['EhrId'],
                'Provider': oxygen_saturation['Provider'],
                'TerraSummaryId': oxygen_saturation['TerraSummaryId'],
                'BloodOxygenSaturation': oxygen_saturation['BloodOxygenSaturation'],
                'Unit': oxygen_saturation['Unit'],
                'RecordDate': oxygen_saturation['RecordDate'],
                'RecordedByUserId': oxygen_saturation['RecordedByUserId'],
            }
            oxygen_saturation = {
                 'UserId': oxygen_saturation['UserId'],
                'TenantId': oxygen_saturation['TenantId'],
                'SessionId': None,
                'ResourceId': oxygen_saturation['id'],
                'ResourceType': "Biometric",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User deleted a blood oxygen saturation.",
                'Attributes': str(attributes),
                'Timestamp': oxygen_saturation['DeletedAt'],
                'UserRegistrationDate': oxygen_saturation['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(oxygen_saturation)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_oxygen_saturation_delete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            oxygen_saturation_records = OxygenSaturationEventsSynchronizer.get_reancare_oxygen_saturation_delete_events(filters)
            if oxygen_saturation_records:
                for oxygen_saturation in oxygen_saturation_records:
                    existing_event = DataSynchronizer.get_existing_event(
                        oxygen_saturation['UserId'], oxygen_saturation['id'], EventType.VitalDeleteOxygenSaturation)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = OxygenSaturationEventsSynchronizer.add_analytics_oxygen_saturation_delete_event(oxygen_saturation)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(oxygen_saturation)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Blood Oxygen Saturation Delete Events found.")
        except Exception as error:
            print(f"Error syncing Blood Oxygen Saturation Delete Events: {error}")

    #endregion

    