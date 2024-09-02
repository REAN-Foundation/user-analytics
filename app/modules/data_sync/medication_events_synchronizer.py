from app.domain_types.enums.event_types import EventType
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class MedicationEventsSynchronizer:

    #region Create Medication events

    @staticmethod
    def get_reancare_medication_create_events():
        try:
            rean_db_connector = DataSynchronizer.get_reancare_db_connector()
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
                medication.CreatedAt
                medication.UpdatedAt,
                medication.DeletedAt,
                user.TenantId,
                user.CreatedAt as UserRegistrationDate
            from medications as medication
            JOIN users as user ON medication.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
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
            user = DataSynchronizer.get_user(medication['UserId'])
            if not user:
                print(f"User not found for the event: {medication}")
                return None
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
                'TenantId': user['TenantId'],
                'SessionId': None,
                'ResourceId': medication['id'],
                'ResourceType': "Medication",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventCategory': "Medication",
                'ActionType': "User-Action",
                'ActionStatement': "User added a medication.",
                'Attributes': str(attributes),
                'Timestamp': medication['CreatedAt'],
                'UserRegistrationDate': user['CreatedAt']
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
    def sync_medication_create_events():
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            meds = MedicationEventsSynchronizer.get_reancare_medication_create_events()
            if meds:
                for med in meds:
                    existing_event = DataSynchronizer.get_existing_event(
                        med['UserId'], med['id'], EventType.MedicationCreate)
                    if existing_event:
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
    def get_reancare_medication_delete_events():
        try:
            rean_db_connector = DataSynchronizer.get_reancare_db_connector()
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
                medication.CreatedAt
                medication.UpdatedAt,
                medication.DeletedAt,
                user.TenantId,
                user.CreatedAt as UserRegistrationDate
            from medications as medication
            JOIN users as user ON medication.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                medication.DeletedAt IS NOT NULL
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
            user = DataSynchronizer.get_user(medication['UserId'])
            if not user:
                print(f"User not found for the event: {medication}")
                return None
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
                'TenantId': user['TenantId'],
                'SessionId': None,
                'ResourceId': medication['id'],
                'ResourceType': "Medication",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventCategory': "Medication",
                'ActionType': "User-Action",
                'ActionStatement': "User deleted a medication.",
                'Attributes': str(attributes),
                'Timestamp': medication['DeletedAt'],
                'UserRegistrationDate': user['CreatedAt']
            }
            new_event_added = DataSynchronizer.add_event(medication)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                print(f"Inserted row into the medications table.")
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert event: {error}")
            return None

    @staticmethod
    def sync_medication_delete_events():
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            deleted_meds = MedicationEventsSynchronizer.get_reancare_medication_delete_events()
            if deleted_meds:
                for med in deleted_meds:
                    existing_event = DataSynchronizer.get_existing_event(
                        med['UserId'], med['id'], EventType.MedicationDelete)
                    if existing_event:
                        existing_event_count += 1
                        new_event = MedicationEventsSynchronizer.add_analytics_medication_delete_event(med)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(med)
                    else:
                        print(f"User not found for the event: {med}")
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
    def get_reancare_medication_schedule_taken_events():
        try:
            rean_db_connector = DataSynchronizer.get_reancare_db_connector()
            query = f"""
            SELECT
                medication_consumption.id,
                medication_consumption.PatientUserId as UserId,
                medication_consumption.MedicationId,
                medication_consumption.IsTaken,
                medication_consumption.TakenAt,
                medication_consumption.DrugName,
                medication_consumption.DrugId,
                medication_consumption.TimeScheduleStart,
                medication_consumption.TimeScheduleEnd,
                medication_consumption.CreatedAt,
                medication_consumption.UpdatedAt,
                medication_consumption.DeletedAt,
                user.TenantId,
                user.CreatedAt as UserRegistrationDate
            from medication_consumptions as medication_consumption
            JOIN users as user ON medication_consumption.PatientUserId = user.id
            WHERE
                DeletedAt IS NULL
                AND
                IsTaken = 1
                AND
                TakenAt IS NOT NULL
            LIMIT 10000
            OFFSET 0
            ORDER BY TakenAt ASC
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Medication Schedule Taken Events:", error)
            return None

    @staticmethod
    def add_analytics_medication_schedule_taken_event(medication_consumption):
        try:
            event_name = EventType.MedicationScheduleTaken.value
            user = DataSynchronizer.get_user(medication_consumption['UserId'])
            if not user:
                print(f"User not found for the event: {medication_consumption}")
                return None
            attributes = {
                'MedicationId': medication_consumption['MedicationId'],
                'IsTaken': medication_consumption['IsTaken'],
                'TakenAt': medication_consumption['TakenAt'],
                'DrugName': medication_consumption['DrugName'],
                'DrugId': medication_consumption['DrugId'],
                'TimeScheduleStart': medication_consumption['TimeScheduleStart'],
                'TimeScheduleEnd': medication_consumption['TimeScheduleEnd']
            }
            event = {
                'UserId': medication_consumption['UserId'],
                'TenantId': user['TenantId'],
                'SessionId': None,
                'ResourceId': medication_consumption['id'],
                'ResourceType': "Medication-Schedule",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventCategory': "Medication-Schedule",
                'ActionType': "User-Action",
                'ActionStatement': "User took a medication.",
                'Attributes': str(attributes),
                'Timestamp': medication_consumption['TakenAt'],
                'UserRegistrationDate': user['CreatedAt']
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
    def sync_medication_schedule_taken_events():
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            taken_meds = MedicationEventsSynchronizer.get_reancare_medication_schedule_taken_events()
            if taken_meds:
                for med in taken_meds:
                    existing_event = DataSynchronizer.get_existing_event(
                        med['UserId'], med['id'], EventType.MedicationScheduleTaken)
                    if existing_event:
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
    def get_reancare_medication_schedule_missed_events():
        try:
            rean_db_connector = DataSynchronizer.get_reancare_db_connector()
            query = f"""
            SELECT
                medication_consumption.id,
                medication_consumption.PatientUserId as UserId,
                medication_consumption.MedicationId,
                medication_consumption.IsTaken,
                medication_consumption.TakenAt,
                medication_consumption.IsMissed,
                medication_consumption.DrugName,
                medication_consumption.DrugId,
                medication_consumption.TimeScheduleStart,
                medication_consumption.TimeScheduleEnd,
                medication_consumption.CreatedAt,
                medication_consumption.UpdatedAt,
                medication_consumption.DeletedAt,
                user.TenantId,
                user.CreatedAt as UserRegistrationDate
            from medication_consumptions as medication_consumption
            JOIN users as user ON medication_consumption.PatientUserId = user.id
            WHERE
                DeletedAt IS NULL
                AND
                IsTaken = 0
                AND
                TakenAt IS NULL
                AND
                IsMissed = 1
            LIMIT 10000
            OFFSET 0
            ORDER BY CreatedAt ASC
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Medication Schedule Missed Events:", error)
            return None

    @staticmethod
    def add_analytics_medication_schedule_missed_event(medication_consumption):
        try:
            event_name = EventType.MedicationScheduleMissed.value
            user = DataSynchronizer.get_user(medication_consumption['UserId'])
            if not user:
                print(f"User not found for the event: {medication_consumption}")
                return None
            attributes = {
                'MedicationId': medication_consumption['MedicationId'],
                'IsTaken': medication_consumption['IsTaken'],
                'TakenAt': medication_consumption['TakenAt'],
                'IsMissed': medication_consumption['IsMissed'],
                'DrugName': medication_consumption['DrugName'],
                'DrugId': medication_consumption['DrugId'],
                'TimeScheduleStart': medication_consumption['TimeScheduleStart'],
                'TimeScheduleEnd': medication_consumption['TimeScheduleEnd']
            }
            event = {
                'UserId': medication_consumption['UserId'],
                'TenantId': user['TenantId'],
                'SessionId': None,
                'ResourceId': medication_consumption['id'],
                'ResourceType': "Medication-Schedule",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventCategory': "Medication-Schedule",
                'ActionType': "User-Action",
                'ActionStatement': "User missed a medication.",
                'Attributes': str(attributes),
                'Timestamp': medication_consumption['UpdatedAt'],
                'UserRegistrationDate': user['CreatedAt']
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
    def sync_medication_schedule_missed_events():
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            missed_meds = MedicationEventsSynchronizer.get_reancare_medication_schedule_missed_events()
            if missed_meds:
                for med in missed_meds:
                    existing_event = DataSynchronizer.get_existing_event(
                        med['UserId'], med['id'], EventType.MedicationScheduleMissed)
                    if existing_event:
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

    #endregion
