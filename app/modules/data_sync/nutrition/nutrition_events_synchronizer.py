from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_subjects import EventSubject
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.data_sync import DataSyncSearchFilter
from app.modules.data_sync.connectors import get_reancare_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
import mysql.connector

############################################################

class NutritionEventsSynchronizer:

    #region Add Nutrition Create events

    @staticmethod
    def get_reancare_nutrition_start_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND nutrition.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                nutrition.id,
                nutrition.EhrId,
                nutrition.PatientUserId as UserId,
                nutrition.Provider,
                nutrition.TerraSummaryId,
                nutrition.Food,
                nutrition.FoodTypes,
                nutrition.Servings,
                nutrition.ServingUnit,
                nutrition.Tags,
                nutrition.UserResponse,
                nutrition.Description,
                nutrition.ConsumedAs,
                nutrition.Calories,
                nutrition.ImageResourceId,
                nutrition.StartTime,
                nutrition.EndTime,
                nutrition.CreatedAt,
                nutrition.UpdatedAt,
                nutrition.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from nutrition_food_consumption as nutrition
            JOIN users as user ON nutrition.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Nutrition Create Events:", error)
            return None

    @staticmethod
    def add_analytics_nutrition_start_event(nutrition):
        try:
            event_name = EventType.NutritionStart.value
            event_category = EventCategory.Nutrition.value
            event_subject = EventSubject.Food.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': nutrition['EhrId'],
                'Provider': nutrition['Provider'],
                'TerraSummaryId': nutrition['TerraSummaryId'],
                'Food': nutrition['Food'],
                'FoodTypes': nutrition['FoodTypes'],
                'Servings': nutrition['Servings'],
                'ServingUnit': nutrition['ServingUnit'],
                'Tags': nutrition['Tags'],
                'UserResponse': nutrition['UserResponse'],
                'Description': nutrition['Description'],
                'ConsumedAs': nutrition['ConsumedAs'],
                'Calories': nutrition['Calories'],
                'ImageResourceId': nutrition['ImageResourceId'],
                'StartTime': nutrition['StartTime'],
                'EndTime': nutrition['EndTime'],
             }
            nutrition = {
                'UserId': nutrition['UserId'],
                'TenantId': nutrition['TenantId'],
                'SessionId': None,
                'ResourceId': nutrition['id'],
                'ResourceType': "nutrition",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User added a nutrition.",
                'Attributes': str(attributes),
                'Timestamp': nutrition['CreatedAt'],
                'UserRegistrationDate': nutrition['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(nutrition)
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
    def sync_nutrition_start_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            nutritions = NutritionEventsSynchronizer.get_reancare_nutrition_start_events(filters)
            if nutritions:
                for nutrition in nutritions:
                    existing_event = DataSynchronizer.get_existing_event(
                        nutrition['UserId'], nutrition['id'], EventType.NutritionStart)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = NutritionEventsSynchronizer.add_analytics_nutrition_start_event(nutrition)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(nutrition)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Nutrition Start Events found.")
        except Exception as error:
            print(f"Error syncing User Nutrition Start Events: {error}")

    #endregion

    #region Update nutrition events

    @staticmethod
    def get_reancare_nutrition_update_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND nutrition.UpdatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                nutrition.id,
                nutrition.EhrId,
                nutrition.PatientUserId as UserId,
                nutrition.Provider,
                nutrition.TerraSummaryId,
                nutrition.Food,
                nutrition.FoodTypes,
                nutrition.Servings,
                nutrition.ServingUnit,
                nutrition.Tags,
                nutrition.UserResponse,
                nutrition.Description,
                nutrition.ConsumedAs,
                nutrition.Calories,
                nutrition.ImageResourceId,
                nutrition.StartTime,
                nutrition.EndTime,
                nutrition.CreatedAt,
                nutrition.UpdatedAt,
                nutrition.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from nutrition_food_consumption as nutrition
            JOIN users as user ON nutrition.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                nutrition.CreatedAt <> nutrition.UpdatedAt
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Nutrition Update Events:", error)
            return None

    @staticmethod
    def add_analytics_nutrition_update_event(nutrition):
        try:
            event_name = EventType.NutritionUpdate.value
            event_category = EventCategory.Nutrition.value
            event_subject = EventSubject.Food.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': nutrition['EhrId'],
                'Provider': nutrition['Provider'],
                'TerraSummaryId': nutrition['TerraSummaryId'],
                'Food': nutrition['Food'],
                'FoodTypes': nutrition['FoodTypes'],
                'Servings': nutrition['Servings'],
                'ServingUnit': nutrition['ServingUnit'],
                'Tags': nutrition['Tags'],
                'UserResponse': nutrition['UserResponse'],
                'Description': nutrition['Description'],
                'ConsumedAs': nutrition['ConsumedAs'],
                'Calories': nutrition['Calories'],
                'ImageResourceId': nutrition['ImageResourceId'],
                'StartTime': nutrition['StartTime'],
                'EndTime': nutrition['EndTime'],
             }
            nutrition = {
                'UserId': nutrition['UserId'],
                'TenantId': nutrition['TenantId'],
                'SessionId': None,
                'ResourceId': nutrition['id'],
                'ResourceType': "nutrition",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User updated a nutrition.",
                'Attributes': str(attributes),
                'Timestamp': nutrition['UpdatedAt'],
                'UserRegistrationDate': nutrition['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(nutrition)
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
    def sync_nutrition_update_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            nutritions = NutritionEventsSynchronizer.get_reancare_nutrition_update_events(filters)
            if nutritions:
                for nutrition in nutritions:
                    existing_event = DataSynchronizer.get_existing_event(
                        nutrition['UserId'], nutrition['id'], EventType.NutritionUpdate)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = NutritionEventsSynchronizer.add_analytics_nutrition_update_event(nutrition)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(nutrition)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Nutrition Update Events found.")
        except Exception as error:
            print(f"Error syncing User Nutrition Update Events: {error}")

    #endregion

    #region Update Symptom events

    @staticmethod
    def get_reancare_nutrition_complete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND nutrition.EndTime between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                nutrition.id,
                nutrition.EhrId,
                nutrition.PatientUserId as UserId,
                nutrition.Provider,
                nutrition.TerraSummaryId,
                nutrition.Food,
                nutrition.FoodTypes,
                nutrition.Servings,
                nutrition.ServingUnit,
                nutrition.Tags,
                nutrition.UserResponse,
                nutrition.Description,
                nutrition.ConsumedAs,
                nutrition.Calories,
                nutrition.ImageResourceId,
                nutrition.StartTime,
                nutrition.EndTime,
                nutrition.CreatedAt,
                nutrition.UpdatedAt,
                nutrition.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from nutrition_food_consumption as nutrition
            JOIN users as user ON nutrition.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                nutrition.EndTime IS NOT null
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Nutrition Complete Events:", error)
            return None

    @staticmethod
    def add_analytics_nutrition_complete_event(nutrition):
        try:
            event_name = EventType.NutritionComplete.value
            event_category = EventCategory.Nutrition.value
            event_subject = EventSubject.Nutrition.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': nutrition['EhrId'],
                'Provider': nutrition['Provider'],
                'TerraSummaryId': nutrition['TerraSummaryId'],
                'Food': nutrition['Food'],
                'FoodTypes': nutrition['FoodTypes'],
                'Servings': nutrition['Servings'],
                'ServingUnit': nutrition['ServingUnit'],
                'Tags': nutrition['Tags'],
                'UserResponse': nutrition['UserResponse'],
                'Description': nutrition['Description'],
                'ConsumedAs': nutrition['ConsumedAs'],
                'Calories': nutrition['Calories'],
                'ImageResourceId': nutrition['ImageResourceId'],
                'StartTime': nutrition['StartTime'],
                'EndTime': nutrition['EndTime'],
             }
            nutrition = {
                'UserId': nutrition['UserId'],
                'TenantId': nutrition['TenantId'],
                'SessionId': None,
                'ResourceId': nutrition['id'],
                'ResourceType': "nutrition",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User added a nutrition.",
                'Attributes': str(attributes),
                'Timestamp': nutrition['EndTime'],
                'UserRegistrationDate': nutrition['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(nutrition)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_nutrition_complete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            nutritions = NutritionEventsSynchronizer.get_reancare_nutrition_complete_events(filters)
            if nutritions:
                for nutrition in nutritions:
                    existing_event = DataSynchronizer.get_existing_event(
                        nutrition['UserId'], nutrition['id'], EventType.NutritionComplete)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = NutritionEventsSynchronizer.add_analytics_nutrition_complete_event(nutrition)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(nutrition)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Nutrition Complete Events found.")
        except Exception as error:
            print(f"Error syncing User Nutrition Complete Events: {error}")

    #endregion

    @staticmethod
    def get_reancare_nutrition_cancel_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND nutrition.DeletedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                nutrition.id,
                nutrition.EhrId,
                nutrition.PatientUserId as UserId,
                nutrition.Provider,
                nutrition.TerraSummaryId,
                nutrition.Food,
                nutrition.FoodTypes,
                nutrition.Servings,
                nutrition.ServingUnit,
                nutrition.Tags,
                nutrition.UserResponse,
                nutrition.Description,
                nutrition.ConsumedAs,
                nutrition.Calories,
                nutrition.ImageResourceId,
                nutrition.StartTime,
                nutrition.EndTime,
                nutrition.CreatedAt,
                nutrition.UpdatedAt,
                nutrition.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from nutrition_food_consumption as nutrition
            JOIN users as user ON nutrition.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                nutrition.DeletedAt IS NOT null
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Nutrition Cancel Events:", error)
            return None

    @staticmethod
    def add_analytics_nutrition_cancel_event(nutrition):
        try:
            event_name = EventType.NutritionCancel.value
            event_category = EventCategory.Nutrition.value
            event_subject = EventSubject.Food.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': nutrition['EhrId'],
                'Provider': nutrition['Provider'],
                'TerraSummaryId': nutrition['TerraSummaryId'],
                'Food': nutrition['Food'],
                'FoodTypes': nutrition['FoodTypes'],
                'Servings': nutrition['Servings'],
                'ServingUnit': nutrition['ServingUnit'],
                'Tags': nutrition['Tags'],
                'UserResponse': nutrition['UserResponse'],
                'Description': nutrition['Description'],
                'ConsumedAs': nutrition['ConsumedAs'],
                'Calories': nutrition['Calories'],
                'ImageResourceId': nutrition['ImageResourceId'],
                'StartTime': nutrition['StartTime'],
                'EndTime': nutrition['EndTime'],
             }
            nutrition = {
                'UserId': nutrition['UserId'],
                'TenantId': nutrition['TenantId'],
                'SessionId': None,
                'ResourceId': nutrition['id'],
                'ResourceType': "nutrition",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User added a nutrition.",
                'Attributes': str(attributes),
                'Timestamp': nutrition['DeletedAt'],
                'UserRegistrationDate': nutrition['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(nutrition)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_nutrition_cancel_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            nutritions = NutritionEventsSynchronizer.get_reancare_nutrition_cancel_events(filters)
            if nutritions:
                for nutrition in nutritions:
                    existing_event = DataSynchronizer.get_existing_event(
                        nutrition['UserId'], nutrition['id'], EventType.NutritionCancel)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = NutritionEventsSynchronizer.add_analytics_nutrition_cancel_event(nutrition)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(nutrition)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Nutrition Cancel Events found.")
        except Exception as error:
            print(f"Error syncing User Nutrition Cancel Events: {error}")
    #endregion


    @staticmethod
    def get_reancare_water_intake_create_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND waterIntake.CreatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                waterIntake.id,
                waterIntake.EhrId,
                waterIntake.PatientUserId as UserId,
                waterIntake.Provider,
                waterIntake.TerraSummaryId,
                waterIntake.Volume,
                waterIntake.Time,
                waterIntake.CreatedAt,
                waterIntake.UpdatedAt,
                waterIntake.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from nutrition_water_consumption as waterIntake
            JOIN users as user ON waterIntake.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Water Intake Create Events:", error)
            return None

    @staticmethod
    def add_analytics_water_intake_create_event(water_intake):
        try:
            event_name = EventType.WaterIntakeAdd.value
            event_category = EventCategory.WaterIntake.value
            event_subject = EventSubject.Water.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': water_intake['EhrId'],
                'PatientUserId': water_intake['UserId'],
                'Provider': water_intake['Provider'],
                'TerraSummaryId': water_intake['TerraSummaryId'],
                'Volume': water_intake['Volume'],
                'Time': water_intake['Time'],
             }
            water_intake = {
                'UserId': water_intake['UserId'],
                'TenantId': water_intake['TenantId'],
                'SessionId': None,
                'ResourceId': water_intake['id'],
                'ResourceType': "water-intake",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User added a water intake.",
                'Attributes': str(attributes),
                'Timestamp': water_intake['CreatedAt'],
                'UserRegistrationDate': water_intake['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(water_intake)
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
    def sync_water_intake_create_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            water_intakes = NutritionEventsSynchronizer.get_reancare_water_intake_create_events(filters)
            if water_intakes:
                for water_intake in water_intakes:
                    existing_event = DataSynchronizer.get_existing_event(
                        water_intake['UserId'], water_intake['id'], EventType.WaterIntakeAdd)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = NutritionEventsSynchronizer.add_analytics_water_intake_create_event(water_intake)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(water_intake)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Water Intake Create Events found.")
        except Exception as error:
            print(f"Error syncing User Water Intake Create Events: {error}")

    #endregion

    #region Update nutrition water intake events

    @staticmethod
    def get_reancare_water_intake_update_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND waterIntake.UpdatedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                waterIntake.id,
                waterIntake.EhrId,
                waterIntake.PatientUserId as UserId,
                waterIntake.Provider,
                waterIntake.TerraSummaryId,
                waterIntake.Volume,
                waterIntake.Time,
                waterIntake.CreatedAt,
                waterIntake.UpdatedAt,
                waterIntake.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from nutrition_water_consumption as waterIntake
            JOIN users as user ON waterIntake.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                waterIntake.CreatedAt <> waterIntake.UpdatedAt
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Water Intake Update Events:", error)
            return None

    @staticmethod
    def add_analytics_water_intake_update_event(water_intake):
        try:
            event_name = EventType.WaterIntakeUpdate.value
            event_category = EventCategory.WaterIntake.value
            event_subject = EventSubject.Water.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': water_intake['EhrId'],
                'PatientUserId': water_intake['UserId'],
                'Provider': water_intake['Provider'],
                'TerraSummaryId': water_intake['TerraSummaryId'],
                'Volume': water_intake['Volume'],
                'Time': water_intake['Time'],
             }
            water_intake = {
                'UserId': water_intake['UserId'],
                'TenantId': water_intake['TenantId'],
                'SessionId': None,
                'ResourceId': water_intake['id'],
                'ResourceType': "water-intake",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "user-action",
                'ActionStatement': "User added a water intake.",
                'Attributes': str(attributes),
                'Timestamp': water_intake['UpdatedAt'],
                'UserRegistrationDate': water_intake['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(water_intake)
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
    def sync_water_intake_update_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            water_intakes = NutritionEventsSynchronizer.get_reancare_water_intake_update_events(filters)
            if water_intakes:
                for water_intake in water_intakes:
                    existing_event = DataSynchronizer.get_existing_event(
                        water_intake['UserId'], water_intake['id'], EventType.WaterIntakeUpdate)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = NutritionEventsSynchronizer.add_analytics_water_intake_update_event(water_intake)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(water_intake)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User Water Intake Update Events found.")
        except Exception as error:
            print(f"Error syncing User Water Intake Update Events: {error}")

    #endregion

    @staticmethod
    def get_reancare_water_intake_delete_events(filters: DataSyncSearchFilter):
        try:
            selection_condition = f"AND waterIntake.DeletedAt between '{filters.StartDate}' AND '{filters.EndDate}'" if filters is not None else ''
            rean_db_connector = get_reancare_db_connector()
            query = f"""
            SELECT
                waterIntake.id,
                waterIntake.EhrId,
                waterIntake.PatientUserId as UserId,
                waterIntake.Provider,
                waterIntake.TerraSummaryId,
                waterIntake.Volume,
                waterIntake.Time,
                waterIntake.CreatedAt,
                waterIntake.UpdatedAt,
                waterIntake.DeletedAt,
                user.id as UserId,
                user.TenantId as TenantId,
                user.CreatedAt as UserRegistrationDate
            from nutrition_water_consumption as waterIntake
            JOIN users as user ON waterIntake.PatientUserId = user.id
            WHERE
                user.IsTestUser = 0
                AND
                waterIntake.DeletedAt IS NOT NULL
                {selection_condition}
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Water Intake Delete Events:", error)
            return None

    @staticmethod
    def add_analytics_water_intake_delete_event(water_intake):
        try:
            event_name = EventType.WaterIntakeDelete.value
            event_category = EventCategory.WaterIntake.value
            event_subject = EventSubject.Water.value
            # user = DataSynchronizer.get_user(medication['UserId'])
            # if not user:
            #     print(f"User not found for the event: {medication}")
            #     return None
            attributes = {
                'EhrId': water_intake['EhrId'],
                'PatientUserId': water_intake['UserId'],
                'Provider': water_intake['Provider'],
                'TerraSummaryId': water_intake['TerraSummaryId'],
                'Volume': water_intake['Volume'],
                'Time': water_intake['Time'],
             }
            water_intake = {
                'UserId': water_intake['UserId'],
                'TenantId': water_intake['TenantId'],
                'SessionId': None,
                'ResourceId': water_intake['id'],
                'ResourceType': "waterintake",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventSubject': event_subject,
                'EventCategory': event_category,
                'ActionType': "User-Action",
                'ActionStatement': "User deleted a waterintake.",
                'Attributes': str(attributes),
                'Timestamp': water_intake['DeletedAt'],
                'UserRegistrationDate': water_intake['UserRegistrationDate']
            }
            new_event_added = DataSynchronizer.add_event(water_intake)
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
    def sync_water_intake_delete_events(filters: DataSyncSearchFilter):
        try:
            existing_event_count = 0
            synched_event_count = 0
            event_not_synched = []
            water_intakes = NutritionEventsSynchronizer.get_reancare_water_intake_delete_events(filters)
            if water_intakes:
                for water_intake in water_intakes:
                    existing_event = DataSynchronizer.get_existing_event(
                        water_intake['UserId'], water_intake['id'], EventType.WaterIntakeDelete)
                    if existing_event is not None:
                        existing_event_count += 1
                    else:
                        new_event = NutritionEventsSynchronizer.add_analytics_water_intake_delete_event(water_intake)
                        if new_event:
                            synched_event_count += 1
                        else:
                            event_not_synched.append(water_intake)
                print(f"Existing Event Count: {existing_event_count}")
                print(f"Synched Event Count: {synched_event_count}")
                print(f"Event Not Synched: {event_not_synched}")
            else:
                print(f"No User WaterInTake Delete Events found.")
        except Exception as error:
            print(f"Error syncing User WaterInTake Delete Events: {error}")

    #endregion
