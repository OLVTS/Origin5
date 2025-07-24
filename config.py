"""
Конфигурация приложения
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Класс конфигурации"""
    
    # Telegram Bot Token
    BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/telegram_bot")
    
    # PostgreSQL connection details
    PGHOST = os.getenv("PGHOST", "localhost")
    PGPORT = os.getenv("PGPORT", "5432")
    PGDATABASE = os.getenv("PGDATABASE", "telegram_bot")
    PGUSER = os.getenv("PGUSER", "postgres")
    PGPASSWORD = os.getenv("PGPASSWORD", "password")
    
    # Админы по умолчанию (можно указать Telegram ID)
    DEFAULT_ADMINS = [int(x) for x in os.getenv("DEFAULT_ADMINS", "").split(",") if x.strip()]
    
    # Настройки аналитики
    ANALYTICS_RETENTION_DAYS = int(os.getenv("ANALYTICS_RETENTION_DAYS", "365"))
    
    # Настройки экспорта
    EXPORT_LIMIT = int(os.getenv("EXPORT_LIMIT", "10000"))
    
    @classmethod
    def get_database_url(cls):
        """Получение URL базы данных"""
        if cls.DATABASE_URL:
            return cls.DATABASE_URL
        else:
            return f"postgresql://{cls.PGUSER}:{cls.PGPASSWORD}@{cls.PGHOST}:{cls.PGPORT}/{cls.PGDATABASE}"
