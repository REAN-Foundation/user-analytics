import os
import mysql.connector

# class DatabaseManager:
class MySQLConnector:
    def __init__(self, host, user, password, database):
        self.database = database
        self.connection = self.create_connection(host, user, password, database)

    def create_connection(self, host, user, password, database):
        """
        Create a database connection using the credentials from the environment.
        """
        # host = os.getenv("DB_HOST")
        # database = os.getenv("DB_NAME")
        # user = os.getenv("DB_USER")
        # password = os.getenv("DB_PASSWORD")

        try:
            connection = mysql.connector.connect(
                host=host,
                database=database,
                user=user,
                password=password
            )
            return connection
        except (Exception, mysql.connector.Error) as error:
            print("Error connecting to the database:", error)
            return None

    # def execute_query(self, query, params=None):
    #     """
    #     Execute a SQL query and return the result.
    #     """
    #     try:
    #         with self.connection.cursor() as cursor:
    #             cursor.execute(query, params)
    #             result = cursor.fetchall()
    #         return result
    #     except (Exception, mysql.connector.Error) as error:
    #         print("Error executing the query:", error)
    #         return None

    def execute_query(self, query, params=None):
        """
        Execute a SQL query and return the result for SELECT queries.
        For INSERT, UPDATE, DELETE queries, commit the transaction.
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                
                # If the query is a SELECT, fetch the result
                if query.strip().upper().startswith("SELECT"):
                    result = cursor.fetchall()
                    return result
                else:
                    # For INSERT, UPDATE, DELETE, commit the transaction
                    self.connection.commit()
                    return cursor.rowcount  # Optionally, return the number of affected rows
                    
        except (Exception, mysql.connector.Error) as error:
            print("Error executing the query:", error)
            return None

        
    def create_db(self):
        # connection = mysql.connector.connect(
        #     host=self.host,
        #     user=self.user,
        #     password=self.password
        # )
        cursor = self.connection.cursor()
        cursor.execute(f'CREATE DATABASE IF NOT EXISTS {self.database}')
        cursor.execute(f'USE {self.database}')
        self.connection.commit()
        cursor.close()
        # connection.close()

    def close_connection(self):
        """
        Close the database connection.
        """
        if self.connection.is_connected():
            try:
                self.connection.close()
                print("Database connection closed.")
            except (Exception, mysql.connector.Error) as error:
                print("Error closing the connection:", error)



# import mysql.connector

# class MySQLConnector:

#     def __init__(self, host, user, password, database):
#         self.host = host
#         self.user = user
#         self.password = password
#         self.database = database

#     def connect(self):
#         return 
    
#     def create_db(self):
#         connection = mysql.connector.connect(
#             host=self.host,
#             user=self.user,
#             password=self.password
#         )
#         cursor = connection.cursor()
#         cursor.execute(f'CREATE DATABASE IF NOT EXISTS {self.database}')
#         cursor.execute(f'USE {self.database}')
#         connection.commit()
#         cursor.close()
#         connection.close()
