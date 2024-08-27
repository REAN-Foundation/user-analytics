import os
import mysql.connector

from app.database.mysql_connector import MySQLConnector

class Seeder:

    _user_id = []

    @staticmethod
    def transfer_users_if_not_exists():
        # Connect to the database
        try:
            db_manager = MySQLConnector(
                    host = os.getenv("DB_HOST"),
                    user = os.getenv("DB_USER_NAME"), 
                    password = os.getenv("DB_USER_PASSWORD"), 
                    database = os.getenv("DB_NAME")
                    )
            
            query = "SELECT id FROM users"
            results = db_manager.execute_query(query)
            for row in results:
                user_id, = row
                Seeder._user_id.append(user_id)
            db_manager.close_connection()
            rows_to_insert = Seeder.fetch_reancare_users_not_in_users()
            Seeder.insert_data_into_users(rows_to_insert)
        except Exception as error:
            print("Error retrieving API keys:", error)
    
        # connection = mysql.connector.connect(
        #     host=host,
        #     user=user,
        #     password=password,
        #     database=database
        # )
        # cursor = connection.cursor()

        # try:
        #     # Step 1: Retrieve all UserId values from users table and store them in a list
        #     cursor.execute("SELECT id FROM users")
        #     user_ids = cursor.fetchall()
        #     user_ids_list = [user_id[0] for user_id in user_ids]  # Flatten the list of tuples to a list of ids

        #     if user_ids_list:
        #         # Step 2: Prepare the SQL query using NOT IN operator with the list of UserId values
        #         format_strings = ','.join(['%s'] * len(user_ids_list))
        #         select_query = f"""
        #         INSERT INTO users (id, name, email)  -- Assuming columns: id, name, email
        #         SELECT ru.id, ru.name, ru.email
        #         FROM reancare_users ru
        #         WHERE ru.id NOT IN ({format_strings});
        #         """

        #         # Step 3: Execute the query with the user_ids_list as the parameter
        #         cursor.execute(select_query, user_ids_list)
        #         connection.commit()
        #         print("Rows successfully transferred where IDs do not exist in the users table.")
        #     else:
        #         # If users table is empty, just copy all rows from reancare_users to users
        #         select_query = """
        #         INSERT INTO users (id, name, email)
        #         SELECT ru.id, ru.name, ru.email
        #         FROM reancare_users ru;
        #         """
        #         cursor.execute(select_query)
        #         connection.commit()
        #         print("All rows from reancare_users were transferred to users table.")

        # except mysql.connector.Error as error:
        #     print(f"Failed to insert records: {error}")
        # finally:
        #     cursor.close()
        #     connection.close()

    @staticmethod
    def fetch_reancare_users_not_in_users():
        # connection = DatabaseOperations.create_connection(host, user, password, database)
        # cursor = connection.cursor()
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
    def fetch_reancare_user_by_user_id(user_id):
        # connection = DatabaseOperations.create_connection(host, user, password, database)
        # cursor = connection.cursor()
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

    
            select_query = f"""
            SELECT user.id, user.TenantId, person.FirstName, person.LastName, person.Gender, person.Email, person.Phone, user.LastLogin, user.RoleId, user.CreatedAt from users as user
            JOIN persons as person ON user.PersonId = person.id
            WHERE 
                user.DeletedAt IS null
                AND
                user.id = "{user_id}"
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
        # connection = DatabaseOperations.create_connection(host, user, password, database)
        # cursor = connection.cursor()

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
        # finally:
            # cursor.close()
            # connection.close()

# Example usage
# host = 'localhost'
# user = 'root'
# password = 'your_password'
# database = 'your_database'

# DatabaseOperations.transfer_users_if_not_exists(host, user, password, database)
