import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


SQLALCHEMY_DATABASE_URL = os.environ.get(
    "SQLALCHEMY_DATABASE_URL",
    "sqlite:///./flowers.db"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Yields a new database session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_tables():
    """Create tables if they do not already exist."""
    from models import Base
    Base.metadata.create_all(bind=engine)
