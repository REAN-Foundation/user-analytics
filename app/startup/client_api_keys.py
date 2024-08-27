import os

from app.database.mysql_connector import MySQLConnector

class APIManager:
    # Static data member to hold the API keys
    _api_keys = []

    @staticmethod
    def load_api_keys():
        """
        Read all the API keys from the database and store them in the static list.
        """
        try:
            # host = os.getenv("REANCARE_DB_HOST")
            # database = os.getenv("REANCARE_DB_NAME")
            # user = os.getenv("REANCARE_DB_USER_NAME")
            # password = os.getenv("REANCARE_DB_USER_PASSWORD")
            db_manager = MySQLConnector(
                host = os.getenv("REANCARE_DB_HOST"),
                user = os.getenv("REANCARE_DB_USER_NAME"), 
                password = os.getenv("REANCARE_DB_USER_PASSWORD"), 
                database = os.getenv("REANCARE_DB_NAME")
                )
            query = "SELECT ApiKey FROM api_clients"
            results = db_manager.execute_query(query)
            for row in results:
                api_key, = row
                APIManager._api_keys.append(api_key)
            db_manager.close_connection()
        except Exception as error:
            print("Error retrieving API keys:", error)

    @staticmethod
    def is_valid_key(api_key):
        """
        Check if the given API key is valid.
        """
        return api_key in APIManager._api_keys
    
# import os
# import requests

# class ClientApiKey:
#     # Static variable to store the API keys
#     api_keys = []

#     @staticmethod
#     def fetch_api_keys():
#         """Fetch API keys from the specified endpoint and store them in the static variable."""
#         try:
#              ClientApiKey.login()
#             # response = requests.get(endpoint_url)
#             # response.raise_for_status()  # Raise an exception for HTTP errors
#             # ApiKeyManager.api_keys = response.json()  # Assuming the response is a JSON list of API keys
#             # print("API keys have been successfully fetched and stored.")
#         except Exception as e:
#             print(f"Failed to fetch API keys: {e}")

#     @staticmethod
#     def login():
#         username = os.getenv('USERNAME')
#         password = os.getenv('PASSWORD')
#         x_api_key = os.getenv('X_API_KEY')
#         base_api_url = os.getenv('BASE_API_URL')

#         if not all([username, password, x_api_key, base_api_url]):
#                 raise ValueError("Missing environment variables: API_USERNAME, API_PASSWORD, or X_API_KEY.")
#         login_payload = {
#                 'UserName': username,
#                 'Password': password,
#                 'LoginRoleId': 1
#             }
            
#             # Login headers
#         login_headers = {
#                 'Content-Type': 'application/json',
#                 'x-api-key': x_api_key
#             }
        
#         login_response = requests.post(base_api_url+'/users/login-with-password', json=login_payload, headers=login_headers)
#         if login_response.status_code != 200:
#              raise Exception('login_response.json().get('Message')')
#         print(f"Login Response = {login_response.json().get('Data').get('AccessToken')}")

# Example usage
# endpoint = "https://example.com/api/keys"
# ClientApiKey.fetch_api_keys(endpoint)
# print(ClientApiKey.api_keys)
