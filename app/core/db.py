# app/core/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.storage.models import Base

# ЛОКАЛЬНАЯ SQLite — работает без Docker
DATABASE_URL = "sqlite:///./microblog.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # требуется для SQLite
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db() -> None:
    """Создание таблиц при запуске"""
    Base.metadata.create_all(bind=engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
