
import os
from app.common.cache import LocalMemoryCache
from app.database.mysql_connector import MySQLConnector

############################################################

reancare_db_host = os.getenv("REANCARE_DB_HOST")
reancare_db_database = os.getenv("REANCARE_DB_NAME")
reancare_db_user = os.getenv("REANCARE_DB_USER_NAME")
reancare_db_password = os.getenv("REANCARE_DB_USER_PASSWORD")

this_db_host = os.getenv("DB_HOST")
this_db_database = os.getenv("DB_NAME")
this_db_user = os.getenv("DB_USER_NAME")
this_db_password = os.getenv("DB_USER_PASSWORD")

############################################################

class DataSyncHandler:

    _tenantCache = LocalMemoryCache()
    _userCache = LocalMemoryCache()
    _apiKeysCache = LocalMemoryCache()

    @staticmethod
    def get_analytics_user(user_id):
        try:
            db_connector = MySQLConnector(this_db_host, this_db_user, this_db_password, this_db_database)
            query = f"""
            SELECT * from users
            WHERE
                id = "{user_id}"
            """
            rows = db_connector.execute_query(query)
            if len(rows) > 0:
                return rows[0]
            else:
                return None
        except Exception as error:
            print("Error retrieving API keys:", error)
            return None

    @staticmethod
    def get_analytics_tenant(tenant_id):
        try:
            db_connector = MySQLConnector(this_db_host, this_db_user, this_db_password, this_db_database)
            query = f"""
            SELECT * from tenants
            WHERE
                id = "{tenant_id}"
            """
            rows = db_connector.execute_query(query)
            if len(rows) > 0:
                return rows[0]
            else:
                return None
        except Exception as error:
            print("Error retrieving API keys:", error)
            return None

    @staticmethod
    def fetch_user_from_reancare(user_id):
        user = None
        try:
            rean_db_connector = MySQLConnector(
                reancare_db_host, reancare_db_user, reancare_db_password, reancare_db_database)
            query = f"""
            SELECT user.id, user.TenantId, person.FirstName, person.LastName, person.Gender, person.Email, person.Phone, user.LastLogin, user.RoleId, user.CreatedAt from users as user
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
    def fetch_tenant_from_reancare(tenant_id):
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
    def fetch_reancare_users_not_in_users():
        rows_to_insert = []

        try:
            db_manager = MySQLConnector(
                    host = os.getenv("REANCARE_DB_HOST"),
                    user = os.getenv("REANCARE_DB_USER_NAME"),
                    password = os.getenv("REANCARE_DB_USER_PASSWORD"),
                    database = os.getenv("REANCARE_DB_NAME")
                    )
            # # Fetch all UserId values from users table
            # cursor.execute("SELECT id FROM users")
            # user_ids = cursor.fetchall()
            # user_ids_list = [user_id[0] for user_id in user_ids]  # Flatten the list of tuples to a list of ids

            if Seeder._user_id:
                # Fetch rows from reancare_users where the id is not in users
                print('type: ', type(Seeder._user_id[0]))
                quoted_id_list = [f"'{id}'" for id in Seeder._user_id]
                format_strings = ','.join(quoted_id_list)
                select_query = f"""
                SELECT user.id, user.TenantId, person.FirstName, person.LastName, person.Gender, person.Email, person.Phone, user.LastLogin, user.RoleId, user.CreatedAt from users as user
                JOIN persons as person ON user.PersonId = person.id
                WHERE
                    user.DeletedAt IS null
                    AND
                    user.id NOT IN ({format_strings})
                """
                print('select query:', select_query)
                rows_to_insert = db_manager.execute_query(select_query)
            else:
                select_query = f"""
                SELECT user.id, user.TenantId, person.FirstName, person.LastName, person.Gender, person.Email, person.Phone, user.LastLogin, user.RoleId, user.CreatedAt from users as user
                JOIN persons as person ON user.PersonId = person.id
                WHERE
                    user.DeletedAt IS null
                """
                print('select query:', select_query)
                rows_to_insert = db_manager.execute_query(select_query)


        except Exception as e:
            print(f"Failed to fetch records: {e}")
        finally:
            db_manager.close_connection()

        return rows_to_insert



    @staticmethod
    def insert_data_into_users(data):

        try:
            db_manager = MySQLConnector(
                    host = os.getenv("DB_HOST"),
                    user = os.getenv("DB_USER_NAME"),
                    password = os.getenv("DB_USER_PASSWORD"),
                    database = os.getenv("DB_NAME")
                    )
            # Insert rows into users table
            # insert_query = "INSERT INTO users (id, name, email) VALUES (%s, %s, %s)"
            insert_query = """
            INSERT INTO users (
            id, TenantId, FirstName, LastName, Gender, Email, Phone, LastActive, Role, RegistrationDate
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            count = 0
            for row in data:
                result = db_manager.execute_query(insert_query, row)
                if result is None:
                    print(f"Not inserted data {row}.")
                else:
                    count = count + 1
                    if f"{row[0]}" not in Seeder._user_id:
                        print('row[0]', row[0])
                        Seeder._user_id.append(f"{row[0]}")

            # rows_to_insert = db_manager.execute_query(insert_query)
            print(f"Inserted {len(data)} rows into the users table.")
            return count

        except mysql.connector.Error as error:
            print(f"Failed to insert records: {error}")
            return 0
