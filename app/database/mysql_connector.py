import mysql.connector

class MySQLConnector:

    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        return 
    
    def create_db(self):
        connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password
        )
        cursor = connection.cursor()
        cursor.execute(f'CREATE DATABASE IF NOT EXISTS {self.database}')
        cursor.execute(f'USE {self.database}')
        connection.commit()
        cursor.close()
        connection.close()
