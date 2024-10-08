import mysql.connector

class MySQLConnector:

    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return connection
        except (Exception, mysql.connector.Error) as error:
            print("Error connecting to the database:", error)
            return None

    def create_db(self):
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute(f'CREATE DATABASE IF NOT EXISTS {self.database}')
        cursor.execute(f'USE {self.database}')
        connection.commit()
        cursor.close()
        connection.close()

    def is_read_only_query(self, query):
        q = query.strip().upper()
        return q.startswith("SELECT") or q.startswith("WITH") or q.find('SELECT') != -1

    def close_connection(self, connection):
        if connection.is_connected():
            connection.close()

    def execute_query(self, query, params=None):
        read_only_query = self.is_read_only_query(query)
        try:
            connection = self.connect()
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                if read_only_query:
                    rows = cursor.fetchall()
                    column_names = [i[0] for i in cursor.description]
                    result = [dict(zip(column_names, row)) for row in rows]
                    cursor.close()
                    self.close_connection(connection)
                    return result
                else:
                    connection.commit()
                    rowcount = cursor.rowcount
                    self.close_connection(connection)
                    cursor.close()
                    return rowcount
        except (Exception, mysql.connector.Error) as error:
            print("Error executing the query:", error)
            if not read_only_query:
                connection.rollback()
            self.close_connection(connection)
            return None

    def execute_read_query(self, query, params=None):
        read_only_query = self.is_read_only_query(query)
        if not read_only_query:
            print("This method is only for read-only queries.")
            return None
        try:
            connection = self.connect()
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                column_names = [i[0] for i in cursor.description]
                result = [dict(zip(column_names, row)) for row in rows]
                cursor.close()
                self.close_connection(connection)
                return result
        except (Exception, mysql.connector.Error) as error:
            print("Error executing the read query:", error)
            self.close_connection(connection)
            return None

    def execute_write_query(self, query, params=None):
        read_only_query = self.is_read_only_query(query)
        if read_only_query:
            print("This method is only for write queries.")
            return None
        try:
            connection = self.connect()
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                connection.commit()
                rowcount = cursor.rowcount
                self.close_connection(connection)
                cursor.close()
                return rowcount
        except (Exception, mysql.connector.Error) as error:
            print("Error executing the write query:", error)
            connection.rollback()
            self.close_connection(connection)
            return None
