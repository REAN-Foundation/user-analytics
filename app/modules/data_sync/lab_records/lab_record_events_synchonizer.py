from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class LabRecordEventsSynchronizer:

    #region Create Lab Record events

    @staticmethod
    def get_reancare_lab_record_create_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND labRecord.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                labRecord.id,
                labRecord.PatientUserId as UserId,
                labRecord.EhrId,
                labRecord.TypeId,
                labRecord.TypeName,
                labRecord.DisplayName,
                labRecord.PrimaryValue,
                labRecord.SecondaryValue,
                labRecord.Unit,
                labRecord.ReportId,
                labRecord.OrderId,
                labRecord.RecordedAt,
                labRecord.CreatedAt,
                labRecord.UpdatedAt,
                labRecord.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from lab_records as labRecord
            JOIN users as user ON labRecord.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Lab Record Create Events:", error)
            return None

    @staticmethod
    def add_analytics_lab_record_create_event(lab_record):
        try:
            event_name = EventType.LabRecordAdd.value
            event_category = EventCategory.LabRecords.value
            event_subject = 'lab-record' + '-' + lab_record['TypeName']
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': lab_record['EhrId'],
                'TypeId': lab_record['TypeId'],
                'TypeName': lab_record['TypeName'],
                'DisplayName': lab_record['DisplayName'],
                'PrimaryValue': lab_record['PrimaryValue'],
                'SecondaryValue': lab_record['SecondaryValue'],
                'Unit': lab_record['Unit'],
                'ReportId': lab_record['ReportId'],
                'OrderId': lab_record['OrderId'],
                'RecordedAt': lab_record['RecordedAt'],
            }
            lab_record = {
                'UserId': lab_record['UserId'],
                'TenantId': lab_record['TenantId'],
                'SessionId': None,
                'ResourceId': lab_record['id'],
                'ResourceType': "lab-record",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User added a lab record.",
                'Attributes': str(attributes),
                'Timestamp': lab_record['CreatedAt'],
                'UserRegistrationDate': lab_record['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(lab_record)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_lab_record_create_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            lab_records = LabRecordEventsSynchronizer.get_reancare_lab_record_create_events(filters)
            if lab_records:
                for lab_record in lab_records:
                    existing_event = DataSynchronizer.get_existing_event(
                        lab_record['UserId'], lab_record['id'], EventType.LabRecordAdd)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = LabRecordEventsSynchronizer.add_analytics_lab_record_create_event(lab_record)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(lab_record)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Lab Record Create Events found.")
        except Exception as error:
            print(f"Error syncing User Lab Record Create Events: {error}")

    #endregion

    #region Delete Lab Record events

    @staticmethod
    def get_reancare_lab_record_delete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND labRecord.DeletedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                labRecord.id,
                labRecord.PatientUserId as UserId,
                labRecord.EhrId,
                labRecord.TypeId,
                labRecord.TypeName,
                labRecord.DisplayName,
                labRecord.PrimaryValue,
                labRecord.SecondaryValue,
                labRecord.Unit,
                labRecord.ReportId,
                labRecord.OrderId,
                labRecord.RecordedAt,
                labRecord.CreatedAt,
                labRecord.UpdatedAt,
                labRecord.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from lab_records as labRecord
            JOIN users as user ON labRecord.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                labRecord.DeletedAt IS NOT NULL
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Lab Record Delete Events:", error)
            return None

    @staticmethod
    def add_analytics_lab_record_delete_event(lab_record):
        try:
            event_name = EventType.LabRecordDelete.value
            event_category = EventCategory.LabRecords.value
            event_subject = 'lab-record' + '-' + lab_record['TypeName']
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': lab_record['EhrId'],
                'TypeId': lab_record['TypeId'],
                'TypeName': lab_record['TypeName'],
                'DisplayName': lab_record['DisplayName'],
                'PrimaryValue': lab_record['PrimaryValue'],
                'SecondaryValue': lab_record['SecondaryValue'],
                'Unit': lab_record['Unit'],
                'ReportId': lab_record['ReportId'],
                'OrderId': lab_record['OrderId'],
                'RecordedAt': lab_record['RecordedAt'],
            }
            lab_record = {
                'UserId': lab_record['UserId'],
                'TenantId': lab_record['TenantId'],
                'SessionId': None,
                'ResourceId': lab_record['id'],
                'ResourceType': "lab-record",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User deleted a lab record.",
                'Attributes': str(attributes),
                'Timestamp': lab_record['DeletedAt'],
                'UserRegistrationDate': lab_record['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(lab_record)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_lab_record_delete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            deleted_lab_records = LabRecordEventsSynchronizer.get_reancare_lab_record_delete_events(filters)
            if deleted_lab_records:
                for lab_record in deleted_lab_records:
                    existing_event = DataSynchronizer.get_existing_event(
                        lab_record['UserId'], lab_record['id'], EventType.LabRecordDelete)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = LabRecordEventsSynchronizer.add_analytics_lab_record_delete_event(lab_record)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(lab_record)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Lab Record Delete Events found.")
        except Exception as error:
            print(f"Error syncing User Lab Record Delete Events: {error}")

    #endregion
