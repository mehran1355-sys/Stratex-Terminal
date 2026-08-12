"""
مدیریت اتصال به دیتابیس
Database Connection Manager
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from contextlib import contextmanager

logger = logging.getLogger(__name__)

Base = declarative_base()

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///data/supplydemand.db")

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class DatabaseManager:
    @staticmethod
    def init_db():
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database ready")

    @staticmethod
    def check_connection() -> bool:
        try:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return False


@contextmanager
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    DatabaseManager.init_db()
