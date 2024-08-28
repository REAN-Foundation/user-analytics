import os

from app.database.mysql_connector import MySQLConnector

class ApiKeyManager:

    _api_keys = [] # Static data member to hold the API keys

    @staticmethod
    def load_api_keys():
        """
        Read all the API keys from the database and store them in the static list.
        """
        try:
            host = os.getenv("REANCARE_DB_HOST")
            database = os.getenv("REANCARE_DB_NAME")
            user = os.getenv("REANCARE_DB_USER_NAME")
            password = os.getenv("REANCARE_DB_USER_PASSWORD")
            db_connector = MySQLConnector(host, user, password, database)

            query = "SELECT ApiKey FROM api_clients"
            results = db_connector.execute_query(query)
            for row in results:
                api_key, = row
                ApiKeyManager._api_keys.append(api_key)
        except Exception as error:
            print("Error retrieving API keys:", error)

    @staticmethod
    def is_valid_key(api_key):
        """
        Check if the given API key is valid.
        """
        return api_key in ApiKeyManager._api_keys
