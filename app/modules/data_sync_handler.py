
import os
from app.common.cache import LocalMemoryCache
from app.database.mysql_connector import MySQLConnector
import mysql.connector

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

    _tenantCache = LocalMemoryCache()
    _userCache = LocalMemoryCache()
    _apiKeysCache = LocalMemoryCache()

    #region User

    @staticmethod
    def get_analytics_user(user_id):
        try:
            analytics_db_connector = MySQLConnector(
                analytics_db_host, analytics_db_user, analytics_db_password, analytics_db_database)
            query = f"""
            SELECT * from users
            WHERE
                id = "{user_id}"
            """
            rows = analytics_db_connector.execute_query(query)
            if len(rows) > 0:
                return rows[0]
            else:
                return None
        except Exception as error:
            print("Error retrieving API keys:", error)
            return None

    @staticmethod
    def get_reancare_user(user_id):
        user = None
        try:
            rean_db_connector = MySQLConnector(
                reancare_db_host, reancare_db_user, reancare_db_password, reancare_db_database)
            query = f"""
            SELECT user.id, user.TenantId, person.BirthDate, person.Gender, user.RoleId, user.CurrentTimeZone, user.CreatedAt from users as user
            JOIN persons as person ON user.PersonId = person.id
            WHERE
                user.DeletedAt IS null
                AND
                user.id = "{user_id}"
            """
            rows = rean_db_connector.execute_query(query)
            if len(rows) > 0:
                user = rows[0]
            else:
                user = None
        except Exception as e:
            print(f"Failed to fetch records: {e}")
        return user

    @staticmethod
    def add_analytics_user(user_id, user):
        try:
            analytics_db_connector = MySQLConnector(
                analytics_db_host, analytics_db_user, analytics_db_password, analytics_db_database)
            insert_query = """
            INSERT INTO users (
            id, TenantId, BirthDate, Gender, Role, RegistrationDate, TimezoneOffsetMin
            ) VALUES (
            %s, %s, %s, %s, %s, %s, %s
            )
            """
            timezoneOffsetMin = 0
            timezone = user['CurrentTimeZone']
            if timezone is not None:
                timezoneOffsetMin = int(timezone.split(":")[0]) * 60 + int(timezone.split(":")[1])
            row = (user['id'], user['TenantId'], user['BirthDate'], user['Gender'], user['RoleId'], user['CreatedAt'], timezoneOffsetMin)
            result = analytics_db_connector.execute_query(insert_query, row)
            if result is None:
                print(f"Not inserted data {row}.")
                return None
            else:
                DataSyncHandler._userCache.set(user_id, result)
                print(f"Inserted row into the users table.")
                return result
        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return None
        except Exception as error:
            print(f"Failed to insert records: {error}")
            return None

    @staticmethod
    def get_user(user_id):
        user = DataSyncHandler._userCache.get(user_id)
        if user is not None:
            return user
        else:
            user = DataSyncHandler.get_analytics_user(user_id)
            if user is not None:
                DataSyncHandler._userCache.set(user_id, user)
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
            analytics_db_connector = MySQLConnector(
                analytics_db_host, analytics_db_user, analytics_db_password, analytics_db_database)
            query = f"""
            SELECT * from tenants
            WHERE
                id = "{tenant_id}"
            """
            rows = analytics_db_connector.execute_query(query)
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
            rean_db_connector = MySQLConnector(
                reancare_db_host, reancare_db_user, reancare_db_password, reancare_db_database)
            query = f"""
            SELECT * from tenants
            WHERE
                id = "{tenant_id}"
            """
            rows = rean_db_connector.execute_query(query)
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
            analytics_db_connector = MySQLConnector(
                analytics_db_host, analytics_db_user, analytics_db_password, analytics_db_database)
            insert_query = """
            INSERT INTO tenants (
            id, TenantName, TenantCode, RegistrationDate
            ) VALUES (
            %s, %s, %s, %s
            )
            """
            row = (tenant['id'], tenant['Name'], tenant['Code'], tenant['CreatedAt'])
            result = analytics_db_connector.execute_query(insert_query, row)
            if result is None:
                print(f"Not inserted data {row}.")
                return None
            else:
                DataSyncHandler._tenantCache.set(tenant_id, result)
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
        tenant = DataSyncHandler._tenantCache.get(tenant_id)
        if tenant is not None:
            return tenant
        else:
            tenant = DataSyncHandler.get_analytics_tenant(tenant_id)
            if tenant is not None:
                DataSyncHandler._tenantCache.set(tenant_id, tenant)
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
            rean_db_connector = MySQLConnector(
                reancare_db_host, reancare_db_user, reancare_db_password, reancare_db_database)
            query = f"""
            SELECT * from api_clients
            WHERE
                DeletedAt IS NULL
            """
            rows = rean_db_connector.execute_query(query)
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
                DataSyncHandler._apiKeysCache.set(key, client_app)

    #endregion
