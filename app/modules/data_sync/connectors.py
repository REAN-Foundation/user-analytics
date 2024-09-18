from dotenv import load_dotenv
import os
from app.database.mysql_connector import MySQLConnector
load_dotenv()

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

def get_reancare_db_connector():
    return MySQLConnector(
        reancare_db_host, reancare_db_user, reancare_db_password, reancare_db_database)

def get_analytics_db_connector():
    return MySQLConnector(
        analytics_db_host, analytics_db_user, analytics_db_password, analytics_db_database)

    #endregion

