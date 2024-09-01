
import os
import uuid
from app.common.cache import LocalMemoryCache
from app.database.mysql_connector import MySQLConnector
import mysql.connector

from app.domain_types.enums.event_types import EventType

############################################################

reancare_db_host     = os.getenv("REANCARE_DB_HOST")
reancare_db_database = os.getenv("REANCARE_DB_NAME")
reancare_db_user     = os.getenv("REANCARE_DB_USER_NAME")
reancare_db_password = os.getenv("REANCARE_DB_USER_PASSWORD")

analytics_db_host     = os.getenv("DB_HOST")
analytics_db_database = os.getenv("DB_NAME")
analytics_db_user     = os.getenv("DB_USER_NAME")
analytics_db_password = os.getenv("DB_USER_PASSWORD")

############################################################

class DataSyncHandler:

    _tenant_cache = LocalMemoryCache()
    _user_cache = LocalMemoryCache()
    _api_keys_cache = LocalMemoryCache()
    _role_type_cache = LocalMemoryCache()

    #region Connectors

    @staticmethod
    def get_reancare_db_connector():
        return MySQLConnector(
            reancare_db_host, reancare_db_user, reancare_db_password, reancare_db_database)

    @staticmethod
    def get_analytics_db_connector():
        return MySQLConnector(
            analytics_db_host, analytics_db_user, analytics_db_password, analytics_db_database)

    #endregion

    #region User roles

    @staticmethod
    def get_reancare_user_roles():
        try:
            rean_db_connector = DataSyncHandler.get_reancare_db_connector()
            query = f"""
            SELECT * from roles
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Roles:", error)
            return None

    @staticmethod
    def populate_role_type_cache():
        roles = DataSyncHandler.get_reancare_user_roles()
        if roles is not None:
            for role in roles:
                DataSyncHandler._role_type_cache.set(role['id'], role)

    #endregion

    #region User

    @staticmethod
    def get_analytics_user(user_id):
        try:
            analytics_db_connector = DataSyncHandler.get_analytics_db_connector()
            query = f"""
            SELECT * from users
            WHERE
                id = "{user_id}"
            """
            rows = analytics_db_connector.execute_read_query(query)
            if len(rows) > 0:
                return rows[0]
            else:
                return None
        except Exception as error:
            print("Error retrieving API keys:", error)
            return None

    @staticmethod
    def get_reancare_user_role(user_id):
        try:
            rean_db_connector = DataSyncHandler.get_reancare_db_connector()
            query = f"""
            SELECT RoleId from users
            WHERE
                id = "{user_id}"
            """
            rows = rean_db_connector.execute_read_query(query)
            if len(rows) > 0:
                role_id = rows[0]['RoleId']
                role = DataSyncHandler._role_type_cache.get(role_id)
                return role
            else:
                return None
        except Exception as error:
            print("Error retrieving User Role:", error)

    @staticmethod
    def get_reancare_user(user_id):
        user = None
        try:
            rean_db_connector = DataSyncHandler.get_reancare_db_connector()
            role = DataSyncHandler.get_reancare_user_role(user_id)
            if role is None:
                return None

            query = f"""
            SELECT
                user.id,
                user.TenantId,
                person.BirthDate,
                person.Gender,
                user.RoleId,
                user.CurrentTimeZone,
                user.CreatedAt,
                health_profile.Race,
                health_profile.Ethnicity,
                health_profile.MajorAilment,
                health_profile.IsSmoker,
                health_profile.IsDrinker,
                health_profile.SubstanceAbuse,
                health_profile.StrokeSurvivorOrCaregiver,
                patient.HealthSystem,
                patient.AssociatedHospital,
                user.DeletedAt
            from users as user
            JOIN persons as person ON user.PersonId = person.id
            JOIN patient_health_profiles as health_profile ON user.id = health_profile.PatientUserId
            JOIN patients as patient ON user.id = patient.UserId
            WHERE
                user.IsTestUser = 0
                AND
                user.id = "{user_id}"
            """
            # KK: Removing 'user.DeletedAt IS null' from where clause to fetch deleted users

            if role['RoleName'] != "Patient": # For non-patient users
                query = f"""
                SELECT
                    user.id,
                    user.TenantId,
                    person.BirthDate,
                    person.Gender,
                    user.RoleId,
                    user.CurrentTimeZone,
                    user.CreatedAt,
                    user.DeletedAt
                from users as user
                JOIN persons as person ON user.PersonId = person.id
                WHERE
                    user.DeletedAt IS null
                    AND
                    user.IsTestUser = 0
                    AND
                    user.id = "{user_id}"
                """
            # KK: Removing 'user.DeletedAt IS null' from where clause to fetch deleted users

            rows = rean_db_connector.execute_read_query(query)
            if len(rows) > 0:
                user = rows[0]
            else:
                user = None
        except Exception as e:
            print(f"Failed to fetch records: {e}")
        return user

    @staticmethod
    def add_analytics_user_record(user_id, user):
        try:
            analytics_db_connector = DataSyncHandler.get_analytics_db_connector()
            insert_query = """
            INSERT INTO users (
                id,
                TenantId,
                RoleId,
                OnboardingSource,
                RegistrationDate,
                TimezoneOffsetMin,
                DeletedAt
            ) VALUES (
            %s, %s, %s, %s, %s, %s, %s
            )
            """
            timezoneOffsetMin = 0
            timezone = user['CurrentTimeZone']
            if timezone is not None:
                timezoneOffsetMin = int(timezone.split(":")[0]) * 60 + int(timezone.split(":")[1])
            deleted_at = None if user['DeletedAt'] is None else user['DeletedAt']
            row = (
                user['id'],
                user['TenantId'],
                user['RoleId'],
                "ReanCare",
                user['CreatedAt'],
                timezoneOffsetMin,
                deleted_at
            )
            result = analytics_db_connector.execute_write_query(insert_query, row)
            if result is None:
                print(f"Not inserted data {row}.")
                return None
            else:
                print(f"Inserted row into the users table.")
                return result
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None
        except Exception as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def add_analytics_user_metadata(user):
        try:
            analytics_db_connector = DataSyncHandler.get_analytics_db_connector()
            insert_query = """
            INSERT INTO user_metadata (
                UserId,
                BirthDate,
                Gender,
                LocationLongitude,
                LocationLatitude,
                OnboardingSource,
                Role,
                Attributes,
                Ethnicity,
                Race,
                HealthSystem,
                Hospital,
                IsCareGiver,
                MajorDiagnosis,
                Smoker,
                Alcoholic,
                SubstanceAbuser
            ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """

            role_name = "Patient"
            role = DataSyncHandler._role_type_cache.get(user["RoleId"])
            if role is not None:
                role_name = role['RoleName']

                row = (
                    user['id'],
                    user['BirthDate'],
                    user['Gender'],
                    0.0,
                    0.0,
                    "ReanCare",
                    role_name,
                    "{}",
                    user["Ethnicity"] if user.get('Ethnicity') is not None else None,
                    user["Race"] if user.get('Race') is not None else None,
                    user["HealthSystem"] if user.get('HealthSystem') is not None else None,
                    user["AssociatedHospital"] if user.get('AssociatedHospital') is not None else None,
                    user["StrokeSurvivorOrCaregiver"] if user.get('StrokeSurvivorOrCaregiver') is not None else None,
                    user["MajorAilment"] if user.get('MajorAilment') is not None else None,
                    user["IsSmoker"] if user.get('IsSmoker') is not None else None,
                    user["IsDrinker"] if user.get('IsDrinker') is not None else None,
                    user["SubstanceAbuse"] if user.get('SubstanceAbuse') is not None else None
                )
            row_count = analytics_db_connector.execute_write_query(insert_query, row)
            if row_count is None:
                print(f"Not inserted metadata {row}.")
                return None
            return row_count
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None
        except Exception as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def add_analytics_user(user_id, user):
        added_row_count = DataSyncHandler.add_analytics_user_record(user_id, user)
        if added_row_count == 1:
            user_metadata = DataSyncHandler.add_analytics_user_metadata(user)
            return user_metadata
        return None

    @staticmethod
    def get_user(user_id):
        user = DataSyncHandler._user_cache.get(user_id)
        if user is not None:
            return user
        else:
            user = DataSyncHandler.get_analytics_user(user_id)
            if user is not None:
                DataSyncHandler._user_cache.set(user_id, user)
                return user
            else:
                user_ = DataSyncHandler.get_reancare_user(user_id)
                if user_ is not None:
                    user = DataSyncHandler.add_analytics_user(user_id, user_)
                    return user
        return None

    #endregion

    #region Tenant

    @staticmethod
    def get_analytics_tenant(tenant_id):
        try:
            analytics_db_connector = DataSyncHandler.get_analytics_db_connector()
            query = f"""
            SELECT * from tenants
            WHERE
                id = "{tenant_id}"
            """
            rows = analytics_db_connector.execute_read_query(query)
            if len(rows) > 0:
                return rows[0]
            else:
                return None
        except Exception as error:
            print("Error retrieving API keys:", error)
            return None

    @staticmethod
    def get_reancare_tenant(tenant_id):
        tenant = None
        try:
            rean_db_connector = DataSyncHandler.get_reancare_db_connector()
            query = f"""
            SELECT * from tenants
            WHERE
                id = "{tenant_id}"
            """
            rows = rean_db_connector.execute_read_query(query)
            if len(rows) > 0:
                tenant = rows[0]
            else:
                tenant = None
        except Exception as e:
            print(f"Failed to fetch records: {e}")
        return tenant

    @staticmethod
    def add_analytics_tenant(tenant_id, tenant):
        try:
            analytics_db_connector = DataSyncHandler.get_analytics_db_connector()
            insert_query = """
            INSERT INTO tenants (
            id, TenantName, TenantCode, RegistrationDate
            ) VALUES (
            %s, %s, %s, %s
            )
            """
            row = (tenant['id'], tenant['Name'], tenant['Code'], tenant['CreatedAt'])
            result = analytics_db_connector.execute_write_query(insert_query, row)
            if result is None:
                print(f"Not inserted data {row}.")
                return None
            else:
                DataSyncHandler._tenant_cache.set(tenant_id, result)
                print(f"Inserted row into the tenants table.")
                return result
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None
        except Exception as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def get_tenant(tenant_id):
        tenant = DataSyncHandler._tenant_cache.get(tenant_id)
        if tenant is not None:
            return tenant
        else:
            tenant = DataSyncHandler.get_analytics_tenant(tenant_id)
            if tenant is not None:
                DataSyncHandler._tenant_cache.set(tenant_id, tenant)
                return tenant
            else:
                tenant_ = DataSyncHandler.get_reancare_tenant(tenant_id)
                if tenant_ is not None:
                    tenant = DataSyncHandler.add_analytics_tenant(tenant_id, tenant_)
                    return tenant
        return None

    #endregion

    #region Client App API Keys

    @staticmethod
    def get_reancare_api_clients():
        try:
            rean_db_connector = DataSyncHandler.get_reancare_db_connector()
            query = f"""
            SELECT * from api_clients
            WHERE
                DeletedAt IS NULL
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving API keys:", error)
            return None

    @staticmethod
    def populate_api_keys_cache():
        api_clients = DataSyncHandler.get_reancare_api_clients()
        if api_clients is not None:
            for api_client in api_clients:
                key = api_client['ApiKey']
                client_app = {
                    'ClientId': api_client['id'],
                    'ClientName': api_client['ClientName'],
                    'ClientCode': api_client['ClientCode'],
                    'IsPrivileged': api_client['IsPrivileged'],
                    'ClientInterfaceType': api_client['ClientInterfaceType'],
                    'ApiKey': api_client['ApiKey'],
                }
                DataSyncHandler._api_keys_cache.set(key, client_app)

    #endregion

    #region User-sync

    @staticmethod
    def get_reancare_user_ids():
        try:
            rean_db_connector = DataSyncHandler.get_reancare_db_connector()
            query = f"""
            SELECT id from users
            WHERE
                IsTestUser = 0
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Ids:", error)
            return None

    @staticmethod
    def sync_users():
        try:
            existing_user_count = 0
            synched_user_count = 0
            user_not_synched = []
            user_ids = DataSyncHandler.get_reancare_user_ids()
            if user_ids is None:
                print("No users found.")
                return None
            for user_id in user_ids:
                if DataSyncHandler._user_cache.get(user_id) is not None:
                    existing_user_count += 1
                    continue
                if DataSyncHandler.get_analytics_user(user_id) is not None:
                    existing_user_count += 1
                    continue
                user = DataSyncHandler.get_reancare_user(user_id)
                if user is not None:
                    DataSyncHandler.add_analytics_user(user_id, user)
                    synched_user_count += 1
                else:
                    user_not_synched.append(user_id)
                    print(f"User {user_id} not synced.")

            print(f"Total users: {len(user_ids)}")
            print(f"Existing users: {existing_user_count}")
            print(f"Synched users: {synched_user_count}")
            print(f"Users not synched: {len(user_not_synched)}")
            return user_not_synched
        except Exception as error:
            print("Error syncing users:", error)
            return None

    #endregion

    #region Tenant-sync

    @staticmethod
    def get_reancare_tenant_ids():
        try:
            rean_db_connector = DataSyncHandler.get_reancare_db_connector()
            query = f"""
            SELECT id from tenants
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving Tenant Ids:", error)
            return None

    @staticmethod
    def sync_tenants():
        try:
            existing_tenant_count = 0
            synched_tenant_count = 0
            tenant_not_synched = []
            tenant_ids = DataSyncHandler.get_reancare_tenant_ids()
            if tenant_ids is None:
                print("No tenants found.")
                return None
            for tenant_id in tenant_ids:
                if DataSyncHandler._tenant_cache.get(tenant_id) is not None:
                    existing_tenant_count += 1
                    continue
                if DataSyncHandler.get_analytics_tenant(tenant_id) is not None:
                    existing_tenant_count += 1
                    continue
                tenant = DataSyncHandler.get_reancare_tenant(tenant_id)
                if tenant is not None:
                    DataSyncHandler.add_analytics_tenant(tenant_id, tenant)
                    synched_tenant_count += 1
                else:
                    tenant_not_synched.append(tenant_id)
                    print(f"Tenant {tenant_id} not synced.")

            print(f"Total tenants: {len(tenant_ids)}")
            print(f"Existing tenants: {existing_tenant_count}")
            print(f"Synched tenants: {synched_tenant_count}")
            print(f"Tenants not synched: {len(tenant_not_synched)}")
            return tenant_not_synched
        except Exception as error:
            print("Error syncing tenants:", error)
            return None

    #endregion

    #region Generic event methods

    @staticmethod
    def get_existing_event(user_id, resource_id, event_type):
        try:
            event_name = event_type.value
            analytics_db_connector = DataSyncHandler.get_analytics_db_connector()
            query = f"""
            SELECT * from events
            WHERE
                UserId = "{user_id}"
                AND
                ResourceId = "{resource_id}"
                AND
                EventName = "{event_name}"
            """
            rows = analytics_db_connector.execute_read_query(query)
            if len(rows) > 0:
                return rows[0]
            else:
                return None
        except Exception as error:
            print("Error retrieving Event:", error)
            return None

    @staticmethod
    def add_event(event):
        try:
            analytics_db_connector = DataSyncHandler.get_analytics_db_connector()
            id_ = str(uuid.uuid4())
            insert_query = """
                INSERT INTO events (
                    id,
                    UserId,
                    TenantId,
                    SessionId,
                    ResourceId,
                    ResourceType,
                    SourceName,
                    SourceVersion,
                    EventName,
                    EventCategory,
                    ActionType,
                    ActionStatement,
                    Attributes,
                    Timestamp,
                    DaysSinceRegistration,
                    TimeOffsetSinceRegistration
                ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            diff = event['Timestamp'] - event['RegistrationDate']
            days_since_registration = diff.days
            time_offset_since_registration_seconds = int(diff.total_seconds())
            row = (
                id_,
                event['UserId'],
                event['TenantId'],
                event['SessionId'],
                event['ResourceId'],
                event['ResourceType'],
                event['SourceName'],
                event['SourceVersion'],
                event['EventName'],
                event['EventCategory'],
                event['ActionType'],
                event['ActionStatement'],
                event['Attributes'],
                event['Timestamp'],
                days_since_registration,
                time_offset_since_registration_seconds,
            )
            result = analytics_db_connector.execute_write_query(insert_query, row)
            if result is None:
                print(f"Not inserted data {row}.")
                return False
            else:
                print(f"Inserted row into the events table.")
                return result == 1 # True if one row inserted
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    #endregion

    #region User login session sync

    @staticmethod
    def get_reancare_user_login_sessions():
        try:
            rean_db_connector = DataSyncHandler.get_reancare_db_connector()
            query = f"""
            SELECT * from user_login_sessions
            WHERE
                DeletedAt IS NULL
            """
            rows = rean_db_connector.execute_read_query(query)
            return rows
        except Exception as error:
            print("Error retrieving User Login Sessions:", error)
            return None

    @staticmethod
    def add_login_session_events(session, user):
        try:
            event_name = EventType.UserLogin.value
            event = {
                'UserId': session['UserId'],
                'TenantId': user['TenantId'],
                'SessionId': session['id'],
                'ResourceId': session['id'],
                'ResourceType': "User-Login-Session",
                'SourceName': "ReanCare",
                'SourceVersion': "Unknown",
                'EventName': event_name,
                'EventCategory': "User-Login-Session",
                'ActionType': "User-Action",
                'ActionStatement': "User logged in.",
                'Attributes': "{}",
                'Timestamp': session['StartedAt'],
                'RegistrationDate': user['CreatedAt']
            }
            new_event_added = DataSyncHandler.add_event(event)
            if not new_event_added:
                print(f"Not inserted data.")
                return None
            else:
                print(f"Inserted row into the user_login_sessions table.")
                return new_event_added
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def sync_user_login_events():
        try:
            existing_session_count = 0
            synched_session_count = 0
            session_not_synched = []
            sessions = DataSyncHandler.get_reancare_user_login_sessions()
            if sessions is None:
                print("No user login sessions found.")
                return None
            for session in sessions:
                existing_event = DataSyncHandler.get_existing_event(session['UserId'], session['id'], EventType.UserLogin)
                if existing_event is not None:
                    existing_session_count += 1
                    continue
                user = DataSyncHandler.get_user(session['UserId'])
                if user is not None:
                    DataSyncHandler.add_login_session_events(session, user)
                    synched_session_count += 1
                else:
                    session_not_synched.append(session['id'])
                    print(f"User login session {session['id']} not synced.")

            print(f"Total user login sessions: {len(sessions)}")
            print(f"Existing user login sessions: {existing_session_count}")
            print(f"Synched user login sessions: {synched_session_count}")
            print(f"User login sessions not synched: {len(session_not_synched)}")
            return session_not_synched
        except Exception as error:
            print("Error syncing user login sessions:", error)
            return None

    #endregion
