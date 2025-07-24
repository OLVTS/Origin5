"""
Настройка и инициализация базы данных
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool
from config import Config
import logging

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Создание движка базы данных
engine = create_engine(
    Config.get_database_url(),
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=300,
    pool_pre_ping=True,
    echo=False
)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Инициализация базы данных"""
    try:
        # Импорт всех моделей для создания таблиц
        from models import User, Post, Analytics, UserActivity, PostTemplate
        
        # Создание всех таблиц
        Base.metadata.create_all(bind=engine)
        
        # Создание админов по умолчанию
        db = SessionLocal()
        try:
            from services.user_service import UserService
            user_service = UserService(db)
            
            for admin_id in Config.DEFAULT_ADMINS:
                user_service.create_or_update_user(
                    telegram_id=admin_id,
                    username="admin",
                    first_name="Admin",
                    is_admin=True
                )
            
            db.commit()
            logger.info("База данных успешно инициализирована")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Ошибка при создании админов по умолчанию: {e}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        raise

def get_session():
    """Получение новой сессии базы данных"""
    return SessionLocal()
