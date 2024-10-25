from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class MedicationEventsSynchronizer:

    #region Create Medication events

    @staticmethod
    def get_reancare_medication_create_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND medication.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                medication.id,
                medication.PatientUserId as UserId,
                medication.DrugName,
                medication.DrugId,
                medication.Dose,
                medication.DosageUnit,
                medication.Frequency,
                medication.FrequencyUnit,
                medication.TimeSchedules,
                medication.Duration,
                medication.DurationUnit,
                medication.StartDate,
                medication.EndDate,
                medication.CreatedAt,
                medication.UpdatedAt,
                medication.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from medications as medication
            JOIN users as user ON medication.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Medication Create Events:", error)
            return None

    @staticmethod
    def add_analytics_medication_create_event(medication):
        try:
            event_name = EventType.MedicationCreate.value
            event_category = EventCategory.Medication.value
            event_subject = EventSubject.Medication.value

            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None

            attributes = {
                'DrugName': medication['DrugName'],
                'DrugId': medication['DrugId'],
                'Dose': medication['Dose'],
                'DosageUnit': medication['DosageUnit'],
                'Frequency': medication['Frequency'],
                'FrequencyUnit': medication['FrequencyUnit'],
                'TimeSchedules': medication['TimeSchedules'],
                'Duration': medication['Duration'],
                'DurationUnit': medication['DurationUnit'],
                'StartDate': medication['StartDate'],
                'EndDate': medication['EndDate']
            }
            medication = {
                'UserId': medication['UserId'],
                'TenantId': medication['TenantId'],
                'SessionId': None,
                'ResourceId': medication['id'],
                'ResourceType': "medication",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User added a medication.",
                'Attributes': str(attributes),
                'Timestamp': medication['CreatedAt'],
                'UserRegistrationDate': medication['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(medication)
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
    def sync_medication_create_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            meds = MedicationEventsSynchronizer.get_reancare_medication_create_events(filters)
            if meds:
                for med in meds:
                    existing_event = DataSynchronizer.get_existing_event(
                        med['UserId'], med['id'], EventType.MedicationCreate)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = MedicationEventsSynchronizer.add_analytics_medication_create_event(med)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(med)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Medication Create Events found.")
        except Exception as error:
            print(f"Error syncing User Medication Create Events: {error}")

    #endregion

    #region Delete Medication events

    @staticmethod
    def get_reancare_medication_delete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND medication.DeletedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                medication.id,
                medication.PatientUserId as UserId,
                medication.DrugName,
                medication.DrugId,
                medication.Dose,
                medication.DosageUnit,
                medication.Frequency,
                medication.FrequencyUnit,
                medication.TimeSchedules,
                medication.Duration,
                medication.DurationUnit,
                medication.StartDate,
                medication.EndDate,
                medication.CreatedAt,
                medication.UpdatedAt,
                medication.DeletedAt,
                user.id as UserId,
                user.TenantId,
                user.CreatedAt as UserRegistrationDate
            from medications as medication
            JOIN users as user ON medication.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                medication.DeletedAt IS NOT NULL
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Medication Delete Events:", error)
            return None

    @staticmethod
    def add_analytics_medication_delete_event(medication):
        try:
            event_name = EventType.MedicationDelete.value
            event_category = EventCategory.Medication.value
            event_subject = EventSubject.Medication.value

            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'DrugName': medication['DrugName'],
                'DrugId': medication['DrugId'],
                'Dose': medication['Dose'],
                'DosageUnit': medication['DosageUnit'],
                'Frequency': medication['Frequency'],
                'FrequencyUnit': medication['FrequencyUnit'],
                'TimeSchedules': medication['TimeSchedules'],
                'Duration': medication['Duration'],
                'DurationUnit': medication['DurationUnit'],
                'StartDate': medication['StartDate'],
                'EndDate': medication['EndDate']
            }
            medication = {
                'UserId': medication['UserId'],
                'TenantId': medication['TenantId'],
                'SessionId': None,
                'ResourceId': medication['id'],
                'ResourceType': "medication",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User deleted a medication.",
                'Attributes': str(attributes),
                'Timestamp': medication['DeletedAt'],
                'UserRegistrationDate': medication['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(medication)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                # print(f"Inserted row into the medications table.")
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_medication_delete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            deleted_meds = MedicationEventsSynchronizer.get_reancare_medication_delete_events(filters)
            if deleted_meds:
                for med in deleted_meds:
                    existing_event = DataSynchronizer.get_existing_event(
                        med['UserId'], med['id'], EventType.MedicationDelete)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = MedicationEventsSynchronizer.add_analytics_medication_delete_event(med)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(med)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Medication Delete Events found.")
        except Exception as error:
            print(f"Error syncing User Medication Delete Events: {error}")

    #endregion

    #region Medication Schedule Taken events

    @staticmethod
    def get_reancare_medication_schedule_taken_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND consumption.TakenAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                consumption.id,
                consumption.PatientUserId as UserId,
                consumption.MedicationId,
                consumption.IsTaken,
                consumption.TakenAt,
                consumption.DrugName,
                consumption.DrugId,
                consumption.TimeScheduleStart,
                consumption.TimeScheduleEnd,
                consumption.CreatedAt,
                consumption.UpdatedAt,
                consumption.DeletedAt,
                user.id as UserId,
                user.TenantId,
                user.CreatedAt as UserRegistrationDate
            from medication_consumptions as consumption
            JOIN users as user ON consumption.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                consumption.DeletedAt IS NULL
                AND
                consumption.IsTaken = 1
                AND
                consumption.TakenAt IS NOT NULL
                {selection_condition}
            ORDER BY consumption.TakenAt ASC
            LIMIT 10000
            OFFSET 0
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Medication Schedule Taken Events:", error)
            return None

    @staticmethod
    def add_analytics_medication_schedule_taken_event(schedule):
        try:
            event_name = EventType.MedicationScheduleTaken.value
            event_category = EventCategory.Medication.value
            event_subject = EventSubject.MedicationSchedule.value
            # user = DataSynchronizer.get_user(medication_consumption['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication_consumption}")
            #     return None
            attributes = {
                'MedicationId': schedule['MedicationId'],
                'IsTaken': schedule['IsTaken'],
                'TakenAt': schedule['TakenAt'],
                'DrugName': schedule['DrugName'],
                'DrugId': schedule['DrugId'],
                'TimeScheduleStart': schedule['TimeScheduleStart'],
                'TimeScheduleEnd': schedule['TimeScheduleEnd']
            }
            event = {
                'UserId': schedule['UserId'],
                'TenantId': schedule['TenantId'],
                'SessionId': None,
                'ResourceId': schedule['id'],
                'ResourceType': "medication-schedule",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User took a medication.",
                'Attributes': str(attributes),
                'Timestamp': schedule['TakenAt'],
                'UserRegistrationDate': schedule['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(event)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                # print(f"Inserted row into the medication_consumptions table.")
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_medication_schedule_taken_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            taken_meds = MedicationEventsSynchronizer.get_reancare_medication_schedule_taken_events(filters)
            if taken_meds:
                for med in taken_meds:
                    existing_event = DataSynchronizer.get_existing_event(
                        med['UserId'], med['id'], EventType.MedicationScheduleTaken)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = MedicationEventsSynchronizer.add_analytics_medication_schedule_taken_event(med)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(med)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Medication Schedule Taken Events found.")
        except Exception as error:
            print(f"Error syncing User Medication Schedule Taken Events: {error}")

    #endregion

    #region Medication Schedule Missed events

    @staticmethod
    def get_reancare_medication_schedule_missed_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND consumption.UpdatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                consumption.id,
                consumption.PatientUserId as UserId,
                consumption.MedicationId,
                consumption.IsTaken,
                consumption.TakenAt,
                consumption.IsMissed,
                consumption.DrugName,
                consumption.DrugId,
                consumption.TimeScheduleStart,
                consumption.TimeScheduleEnd,
                consumption.CreatedAt,
                consumption.UpdatedAt,
                consumption.DeletedAt,
                user.id as UserId,
                user.TenantId,
                user.CreatedAt as UserRegistrationDate
            from medication_consumptions as consumption
            JOIN users as user ON consumption.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                consumption.DeletedAt IS NULL
                AND
                consumption.IsTaken = 0
                AND
                consumption.TakenAt IS NULL
                AND
                consumption.IsMissed = 1
                {selection_condition}
            ORDER BY consumption.CreatedAt ASC
            LIMIT 10000
            OFFSET 0
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Medication Schedule Missed Events:", error)
            return None

    @staticmethod
    def add_analytics_medication_schedule_missed_event(schedule):
        try:
            event_name = EventType.MedicationScheduleMissed.value
            event_category = EventCategory.Medication.value
            event_subject = EventSubject.MedicationSchedule.value
            # user = DataSynchronizer.get_user(schedule['UserId'])
            # if not user:
            #     print(f"User not found for the event: {schedule}")
            #     return None
            attributes = {
                'MedicationId': schedule['MedicationId'],
                'IsTaken': schedule['IsTaken'],
                'TakenAt': schedule['TakenAt'],
                'IsMissed': schedule['IsMissed'],
                'DrugName': schedule['DrugName'],
                'DrugId': schedule['DrugId'],
                'TimeScheduleStart': schedule['TimeScheduleStart'],
                'TimeScheduleEnd': schedule['TimeScheduleEnd']
            }
            event = {
                'UserId': schedule['UserId'],
                'TenantId': schedule['TenantId'],
                'SessionId': None,
                'ResourceId': schedule['id'],
                'ResourceType': "medication-schedule",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User missed a medication.",
                'Attributes': str(attributes),
                'Timestamp': schedule['UpdatedAt'],
                'UserRegistrationDate': schedule['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(event)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                # print(f"Inserted row into the medication_consumptions table.")
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_medication_schedule_missed_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            missed_meds = MedicationEventsSynchronizer.get_reancare_medication_schedule_missed_events(filters)
            if missed_meds:
                for med in missed_meds:
                    existing_event = DataSynchronizer.get_existing_event(
                        med['UserId'], med['id'], EventType.MedicationScheduleMissed)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = MedicationEventsSynchronizer.add_analytics_medication_schedule_missed_event(med)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(med)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Medication Schedule Missed Events found.")
        except Exception as error:
            print(f"Error syncing User Medication Schedule Missed Events: {error}")

    #region Medication Consumption Create events

    @staticmethod
    def get_reancare_medication_consumption_create_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND medication_consumption.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                medication_consumption.id,
                medication_consumption.EhrId,
                medication_consumption.PatientUserId,
                medication_consumption.MedicationId,
                medication_consumption.DrugName,
                medication_consumption.DrugId,
                medication_consumption.Dose,
                medication_consumption.Details,
                medication_consumption.TimeScheduleStart,
                medication_consumption.TimeScheduleEnd,
                medication_consumption.TakenAt,
                medication_consumption.IsTaken,
                medication_consumption.IsMissed,
                medication_consumption.IsCancelled,
                medication_consumption.CancelledOn,
                medication_consumption.Note,
                medication_consumption.CreatedAt,
                medication_consumption.UpdatedAt,
                medication_consumption.DeletedAt,
                user.id as UserId,
                user.TenantId,
                user.CreatedAt as UserRegistrationDate
            FROM medication_consumptions as medication_consumption
            JOIN users user on medication_consumption.PatientUserId = user.id
            WHERE 
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Medication Consumption Create Events:", error)
            return None

    @staticmethod
    def add_analytics_medication_consumption_create_event(medication):
        try:
            event_name = EventType.MedicationConsumptionCreate.value
            event_category = EventCategory.Medication.value
            event_subject = f"{medication['DrugName']}"

            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None

            attributes = {
                'DrugName': medication['DrugName'],
                'DrugId': medication['DrugId'],
                'Dose': medication['Dose'],
                'Details': medication['Details'],
                'TimeScheduleStart': medication['TimeScheduleStart'],
                'TimeScheduleEnd': medication['TimeScheduleEnd'],
                'TakenAt': medication['TakenAt'],
                'IsTaken': medication['IsTaken'],
                'IsMissed': medication['IsMissed'],
                'IsCancelled': medication['IsCancelled'],
                'CancelledOn': medication['CancelledOn'],
                'Note': medication['Note']
            }
            medication = {
                'UserId': medication['UserId'],
                'TenantId': medication['TenantId'],
                'SessionId': None,
                'ResourceId': medication['id'],
                'ResourceType': "medication",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "medication-consumption record is created.",
                'Attributes': str(attributes),
                'Timestamp': medication['CreatedAt'],
                'UserRegistrationDate': medication['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(medication)
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
    def sync_medication_consumption_create_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            meds = MedicationEventsSynchronizer.get_reancare_medication_consumption_create_events(filters)
            if meds:
                for med in meds:
                    existing_event = DataSynchronizer.get_existing_event(
                        med['UserId'], med['id'], EventType.MedicationConsumptionCreate)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = MedicationEventsSynchronizer.add_analytics_medication_consumption_create_event(med)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(med)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Medication Consumption Create Events found.")
        except Exception as error:
            print(f"Error syncing User Medication Consumption Create Events: {error}")

    #endregion

#region Medication Consumption Delete events

    @staticmethod
    def get_reancare_medication_consumption_delete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND medication_consumption.DeletedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                medication_consumption.id,
                medication_consumption.EhrId,
                medication_consumption.PatientUserId,
                medication_consumption.MedicationId,
                medication_consumption.DrugName,
                medication_consumption.DrugId,
                medication_consumption.Dose,
                medication_consumption.Details,
                medication_consumption.TimeScheduleStart,
                medication_consumption.TimeScheduleEnd,
                medication_consumption.TakenAt,
                medication_consumption.IsTaken,
                medication_consumption.IsMissed,
                medication_consumption.IsCancelled,
                medication_consumption.CancelledOn,
                medication_consumption.Note,
                medication_consumption.CreatedAt,
                medication_consumption.UpdatedAt,
                medication_consumption.DeletedAt,
                user.id as UserId,
                user.TenantId,
                user.CreatedAt as UserRegistrationDate
            FROM medication_consumptions as medication_consumption
            JOIN users user on medication_consumption.PatientUserId = user.id
            WHERE 
                user.IsTestUser = 0
                AND
                medication_consumption.DeletedAt is not null
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Medication Consumption Delete Events:", error)
            return None

    @staticmethod
    def add_analytics_medication_consumption_delete_event(medication):
        try:
            event_name = EventType.MedicationConsumptionDelete.value
            event_category = EventCategory.Medication.value
            event_subject = f"{medication['DrugName']}"

            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None

            attributes = {
                'DrugName': medication['DrugName'],
                'DrugId': medication['DrugId'],
                'Dose': medication['Dose'],
                'Details': medication['Details'],
                'TimeScheduleStart': medication['TimeScheduleStart'],
                'TimeScheduleEnd': medication['TimeScheduleEnd'],
                'TakenAt': medication['TakenAt'],
                'IsTaken': medication['IsTaken'],
                'IsMissed': medication['IsMissed'],
                'IsCancelled': medication['IsCancelled'],
                'CancelledOn': medication['CancelledOn'],
                'Note': medication['Note']
            }
            medication = {
                'UserId': medication['UserId'],
                'TenantId': medication['TenantId'],
                'SessionId': None,
                'ResourceId': medication['id'],
                'ResourceType': "medication",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "medication-consumption record is deleted.",
                'Attributes': str(attributes),
                'Timestamp': medication['DeletedAt'],
                'UserRegistrationDate': medication['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(medication)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_medication_consumption_delete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            meds = MedicationEventsSynchronizer.get_reancare_medication_consumption_delete_events(filters)
            if meds:
                for med in meds:
                    existing_event = DataSynchronizer.get_existing_event(
                        med['UserId'], med['id'], EventType.MedicationConsumptionDelete)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = MedicationEventsSynchronizer.add_analytics_medication_consumption_delete_event(med)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(med)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Medication Consumption Delete Events found.")
        except Exception as error:
            print(f"Error syncing User Medication Consumption Delete Events: {error}")

    #endregion
