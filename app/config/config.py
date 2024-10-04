from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings
from functools import lru_cache

load_dotenv(find_dotenv('.env'))
class Settings(BaseSettings):

    # App
    ENVIRONMENT              : str = "development"
    SERVICE_NAME             : str = "User-Analytics-Service"
    BASE_URL                 : str = "http://localhost:23456"
    USER_ACCESS_TOKEN_SECRET : str = "secret"
    USER_REFRESH_TOKEN_SECRET: str = "secret"
    CIPHER_SALT              : str = "salt"
    SERVICE_IDENTIFIER       : str = f"{SERVICE_NAME}-{ENVIRONMENT}"

    API_VERSION : str = "0.0.1"
    API_PREFIX  : str = "/api/v1"
    PORT        : int = 23456
    SERVICE_NAME: str = "User-Analytics-Service"

    #Database
    DB_USER_NAME    : str = "dbuser"
    DB_USER_PASSWORD: str = "dbpassword"
    DB_HOST         : str = "localhost"
    DB_PORT         : int = 3306
    DB_NAME         : str = "user_analytics"
    DB_POOL_SIZE    : int = 10
    DB_POOL_RECYCLE : int = 1800
    DB_POOL_TIMEOUT : int = 30
    DB_DIALECT      : str = "mysql"
    DB_DRIVER       : str = "pymysql"
    DB_CONNECTION_STRING: str = f"{DB_DIALECT}+{DB_DRIVER}://{DB_USER_NAME}:{DB_USER_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


    REANCARE_DB_HOST         : str = "localhost"
    REANCARE_DB_NAME         : str = "reancare"
    REANCARE_DB_USER_NAME    : str = "root"
    REANCARE_DB_USER_PASSWORD: str = "root"

    # Open-telemetry
    TRACING_ENABLED           : bool = False
    TRACING_EXPORTER_TYPE     : str  = 'NoExporter'
    TRACING_COLLECTOR_ENDPOINT: str  = 'http://localhost:4317'
    JAEGER_AGENT_HOST         : str  = "localhost"
    JAEGER_AGENT_PORT         : int  = 6831
    METRICS_ENABLED           : bool = False

    AWS_ACCESS_KEY_ID    : str = 'AWS_ACCESS_KEY_ID'
    AWS_SECRET_ACCESS_KEY: str = 'AWS_SECRET_ACCESS_KEY'
    AWS_REGION           : str = 'AWS_REGION'
    AWS_BUCKET           : str = 'AWS_BUCKET'

    LOCAL_STORAGE_PATH: str = "./../storage-uploads"

    AZURE_STORAGE_CONNECTION_STRING: str = 'unspecified'
    AZURE_CONTAINER_NAME           : str = 'unspecified'

    class Config:
        env_file = ".env"
        extra="forbid"

@lru_cache()
def get_settings():
    return Settings()
