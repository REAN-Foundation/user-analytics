from app.config.config import get_settings
from app.database.db_connector import DatabaseConnector

############################################################

settings = get_settings()

print(
    f"[connectors] analytics DB -> dialect={settings.DB_DIALECT} host={settings.DB_HOST} "
    f"port={settings.DB_PORT} db={settings.DB_NAME} | "
    f"reancare DB -> dialect={settings.REANCARE_DB_DIALECT} host={settings.REANCARE_DB_HOST} "
    f"port={settings.REANCARE_DB_PORT} db={settings.REANCARE_DB_NAME}"
)

############################################################

def get_reancare_db_connector():
    return DatabaseConnector(
        settings.REANCARE_DB_HOST,
        settings.REANCARE_DB_USER_NAME,
        settings.REANCARE_DB_USER_PASSWORD,
        settings.REANCARE_DB_NAME,
        port=settings.REANCARE_DB_PORT,
        dialect=settings.REANCARE_DB_DIALECT,
        driver=settings.REANCARE_DB_DRIVER)

def get_analytics_db_connector():
    return DatabaseConnector(
        settings.DB_HOST,
        settings.DB_USER_NAME,
        settings.DB_USER_PASSWORD,
        settings.DB_NAME,
        port=settings.DB_PORT,
        dialect=settings.DB_DIALECT,
        driver=settings.DB_DRIVER)

    #endregion
