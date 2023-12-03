from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config.config import get_settings
from .base import Base
from .mysql_connector import MySQLConnector

###############################################################################

settings = get_settings()

print(settings.DB_CONNECTION_STRING)
connector = MySQLConnector(
    host=settings.DB_HOST,
    user=settings.DB_USER_NAME,
    password=settings.DB_USER_PASSWORD,
    database=settings.DB_NAME
)
connector.create_db()

engine = create_engine(settings.DB_CONNECTION_STRING, echo=False)
# or
# engine = create_engine(
#     settings.DB_DIALECT,
#     username=settings.DB_USER_NAME,
#     password=settings.DB_USER_PASSWORD,
#     host=settings.DB_HOST,
#     port=settings.DB_PORT,
#     database=settings.DB_NAME,
#     pool_size=settings.DB_POOL_SIZE,
#     pool_recycle=settings.DB_POOL_RECYCLE,
#     drivername=settings.DB_DRIVER,
#     echo=True,
# )

Base.metadata.create_all(bind=engine, checkfirst=True)

LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session()-> Session:
    return LocalSession()
