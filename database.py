from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

POSTGRESQL_DATABASE_URL = (
    "postgresql://todoapp_free_postgresql_db_user:"
    "aDimwd5PdVL2JvVeOeeB53OWDXvosD9j@"
    "dpg-churvkfdvk4olisqgkj0-a/todoapp_free_postgresql_db"
)
engine = create_engine(
    POSTGRESQL_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
