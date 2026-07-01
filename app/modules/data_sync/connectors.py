from dotenv import load_dotenv
import os
from app.database.db_connector import DatabaseConnector
load_dotenv()

############################################################

# The source (REANCARE) database is always MySQL.
reancare_db_host     = os.getenv("REANCARE_DB_HOST")
reancare_db_database = os.getenv("REANCARE_DB_NAME")
reancare_db_user     = os.getenv("REANCARE_DB_USER_NAME")
reancare_db_password = os.getenv("REANCARE_DB_USER_PASSWORD")

# The analytics (destination) database follows DB_DIALECT (mysql or postgresql).
analytics_db_host     = os.getenv("DB_HOST")
analytics_db_database = os.getenv("DB_NAME")
analytics_db_user     = os.getenv("DB_USER_NAME")
analytics_db_password = os.getenv("DB_USER_PASSWORD")
analytics_db_port     = os.getenv("DB_PORT")
analytics_db_dialect  = os.getenv("DB_DIALECT", "mysql")
analytics_db_driver   = os.getenv("DB_DRIVER")

############################################################

def get_reancare_db_connector():
    return DatabaseConnector(
        reancare_db_host, reancare_db_user, reancare_db_password, reancare_db_database,
        dialect="mysql")

def get_analytics_db_connector():
    return DatabaseConnector(
        analytics_db_host, analytics_db_user, analytics_db_password, analytics_db_database,
        port=analytics_db_port, dialect=analytics_db_dialect, driver=analytics_db_driver)

    #endregion

