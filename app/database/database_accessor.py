from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config.config import get_settings
from .base import Base
from . import models  
from .db_connector import DatabaseConnector

###############################################################################

settings = get_settings()

print(settings.DB_CONNECTION_STRING)
connector = DatabaseConnector(
    host=settings.DB_HOST,
    user=settings.DB_USER_NAME,
    password=settings.DB_USER_PASSWORD,
    database=settings.DB_NAME,
    port=settings.DB_PORT,
    dialect=settings.DB_DIALECT,
    driver=settings.DB_DRIVER,
)
connector.create_db()

engine = create_engine(
    settings.DB_CONNECTION_STRING,
    pool_size=settings.DB_POOL_SIZE,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,
    echo=False,
)

Base.metadata.create_all(bind=engine, checkfirst=True)

LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session()-> Session:
    return LocalSession()
