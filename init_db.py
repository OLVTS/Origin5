"""
Скрипт инициализации базы данных и миграций
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Добавляем корневую папку в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from database import Base, engine
from models import User, Post, UserActivity, Analytics, PostTemplate
from services.user_service import UserService
from services.analytics_service import AnalyticsService
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_database_connection():
    """Проверка подключения к базе данных"""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("✅ Подключение к базе данных успешно")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к базе данных: {e}")
        return False

def create_database_schema():
    """Создание схемы базы данных"""
    try:
        logger.info("🔧 Создание схемы базы данных...")
        
        # Создание всех таблиц
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Схема базы данных создана успешно")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка при создании схемы: {e}")
        return False

def check_existing_tables():
    """Проверка существующих таблиц"""
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        expected_tables = ['users', 'posts', 'user_activities', 'analytics', 'post_templates']
        
        logger.info(f"📋 Существующие таблицы: {existing_tables}")
        
        missing_tables = [table for table in expected_tables if table not in existing_tables]
        if missing_tables:
            logger.warning(f"⚠️ Отсутствующие таблицы: {missing_tables}")
        else:
            logger.info("✅ Все необходимые таблицы присутствуют")
        
        return existing_tables
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке таблиц: {e}")
        return []

def create_default_admins():
    """Создание администраторов по умолчанию"""
    if not Config.DEFAULT_ADMINS:
        logger.info("ℹ️ Администраторы по умолчанию не указаны в конфигурации")
        return True
    
    try:
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            user_service = UserService(db)
            
            created_admins = []
            for admin_id in Config.DEFAULT_ADMINS:
                try:
                    # Проверяем, существует ли уже администратор
                    existing_user = user_service.get_user_by_telegram_id(admin_id)
                    
                    if existing_user:
                        if not existing_user.is_admin:
                            existing_user.is_admin = True
                            logger.info(f"👑 Пользователь {admin_id} назначен администратором")
                        else:
                            logger.info(f"ℹ️ Пользователь {admin_id} уже является администратором")
                    else:
                        # Создаем нового администратора
                        admin_user = user_service.create_or_update_user(
                            telegram_id=admin_id,
                            username="admin",
                            first_name="Administrator",
                            is_admin=True
                        )
                        created_admins.append(admin_id)
                        logger.info(f"👑 Создан администратор с ID: {admin_id}")
                
                except Exception as e:
                    logger.error(f"❌ Ошибка при создании администратора {admin_id}: {e}")
            
            db.commit()
            
            if created_admins:
                logger.info(f"✅ Создано администраторов: {len(created_admins)}")
            
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Ошибка при создании администраторов: {e}")
            return False
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Ошибка при подключении для создания администраторов: {e}")
        return False

def create_default_templates():
    """Создание шаблонов постов по умолчанию"""
    try:
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            from utils.templates import get_post_templates
            
            # Получаем шаблоны
            templates_data = get_post_templates()
            
            created_templates = []
            updated_templates = []
            
            for template_data in templates_data:
                # Проверяем, существует ли шаблон
                existing_template = db.query(PostTemplate).filter(
                    PostTemplate.name == template_data['name']
                ).first()
                
                template_fields = {
                    'id': template_data['id'],
                    'description': template_data['description'],
                    'icon': template_data['icon'],
                    'content_template': template_data['content_template']
                }
                
                if existing_template:
                    # Обновляем существующий шаблон
                    existing_template.description = template_data['description']
                    existing_template.template_fields = template_fields
                    existing_template.updated_at = datetime.utcnow()
                    updated_templates.append(template_data['name'])
                else:
                    # Создаем новый шаблон
                    new_template = PostTemplate(
                        name=template_data['name'],
                        description=template_data['description'],
                        template_fields=template_fields,
                        is_active=True,
                        usage_count=0
                    )
                    db.add(new_template)
                    created_templates.append(template_data['name'])
            
            db.commit()
            
            logger.info(f"✅ Создано шаблонов: {len(created_templates)}")
            logger.info(f"🔄 Обновлено шаблонов: {len(updated_templates)}")
            
            if created_templates:
                logger.info(f"📋 Новые шаблоны: {', '.join(created_templates)}")
            
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Ошибка при создании шаблонов: {e}")
            return False
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Ошибка при подключении для создания шаблонов: {e}")
        return False

def create_initial_analytics():
    """Создание начальных записей аналитики"""
    try:
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            analytics_service = AnalyticsService(db)
            
            # Создаем начальные метрики
            initial_metrics = [
                ('system_init', 1, {'timestamp': datetime.utcnow().isoformat(), 'version': '1.0'}),
                ('database_schema_version', 1, {'version': '1.0', 'created_at': datetime.utcnow().isoformat()}),
                ('total_users', 0, {'initial_count': 0}),
                ('total_posts', 0, {'initial_count': 0})
            ]
            
            for metric_name, metric_value, metric_data in initial_metrics:
                # Проверяем, существует ли уже такая метрика
                existing_metric = db.query(Analytics).filter(
                    Analytics.metric_name == metric_name
                ).first()
                
                if not existing_metric:
                    analytics_service.save_metric(metric_name, metric_value, metric_data)
                    logger.info(f"📊 Создана метрика: {metric_name}")
            
            db.commit()
            logger.info("✅ Начальная аналитика создана")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Ошибка при создании аналитики: {e}")
            return False
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Ошибка при подключении для создания аналитики: {e}")
        return False

def create_indexes():
    """Создание дополнительных индексов для оптимизации"""
    try:
        with engine.connect() as connection:
            # Список дополнительных индексов
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);",
                "CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);",
                "CREATE INDEX IF NOT EXISTS idx_users_admin ON users(is_admin);",
                "CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author_id);",
                "CREATE INDEX IF NOT EXISTS idx_posts_published ON posts(is_published);",
                "CREATE INDEX IF NOT EXISTS idx_posts_deleted ON posts(is_deleted);",
                "CREATE INDEX IF NOT EXISTS idx_posts_template ON posts(template_type);",
                "CREATE INDEX IF NOT EXISTS idx_activities_user ON user_activities(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_activities_type ON user_activities(activity_type);",
                "CREATE INDEX IF NOT EXISTS idx_activities_timestamp ON user_activities(timestamp);",
                "CREATE INDEX IF NOT EXISTS idx_analytics_metric ON analytics(metric_name);",
                "CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics(date);"
            ]
            
            for index_sql in indexes:
                try:
                    connection.execute(text(index_sql))
                    logger.info(f"✅ Создан индекс: {index_sql.split('idx_')[1].split(' ')[0] if 'idx_' in index_sql else 'unknown'}")
                except Exception as e:
                    logger.warning(f"⚠️ Не удалось создать индекс: {e}")
            
            connection.commit()
            
        logger.info("✅ Индексы созданы")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при создании индексов: {e}")
        return False

def verify_database_integrity():
    """Проверка целостности базы данных"""
    try:
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            # Проверяем количество записей в основных таблицах
            users_count = db.query(User).count()
            posts_count = db.query(Post).count()
            activities_count = db.query(UserActivity).count()
            analytics_count = db.query(Analytics).count()
            templates_count = db.query(PostTemplate).count()
            
            logger.info(f"📊 Статистика базы данных:")
            logger.info(f"   👥 Пользователи: {users_count}")
            logger.info(f"   📝 Посты: {posts_count}")
            logger.info(f"   📈 Активности: {activities_count}")
            logger.info(f"   📊 Аналитика: {analytics_count}")
            logger.info(f"   📋 Шаблоны: {templates_count}")
            
            # Проверяем наличие администраторов
            admins_count = db.query(User).filter(User.is_admin == True).count()
            logger.info(f"   👑 Администраторы: {admins_count}")
            
            if admins_count == 0:
                logger.warning("⚠️ В системе нет администраторов!")
            
            if templates_count == 0:
                logger.warning("⚠️ В системе нет шаблонов постов!")
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке целостности БД: {e}")
        return False

def backup_database():
    """Создание резервной копии базы данных (если поддерживается)"""
    try:
        # Для PostgreSQL можно использовать pg_dump
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{backup_dir}/backup_{timestamp}.sql"
        
        # Простое логирование - реальный backup требует pg_dump
        logger.info(f"💾 Резервная копия может быть создана в: {backup_file}")
        logger.info("💡 Для создания полной резервной копии используйте pg_dump")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при создании резервной копии: {e}")
        return False

def run_migration():
    """Запуск полной миграции"""
    logger.info("🚀 Начало инициализации базы данных...")
    
    steps = [
        ("Проверка подключения к БД", check_database_connection),
        ("Проверка существующих таблиц", check_existing_tables),
        ("Создание схемы БД", create_database_schema),
        ("Создание индексов", create_indexes),
        ("Создание администраторов", create_default_admins),
        ("Создание шаблонов постов", create_default_templates),
        ("Создание начальной аналитики", create_initial_analytics),
        ("Проверка целостности БД", verify_database_integrity),
        ("Создание резервной копии", backup_database)
    ]
    
    success_count = 0
    
    for step_name, step_function in steps:
        logger.info(f"▶️ {step_name}...")
        try:
            if step_function():
                success_count += 1
                logger.info(f"✅ {step_name} - выполнено")
            else:
                logger.error(f"❌ {step_name} - ошибка")
        except Exception as e:
            logger.error(f"❌ {step_name} - исключение: {e}")
    
    logger.info(f"📋 Выполнено шагов: {success_count}/{len(steps)}")
    
    if success_count == len(steps):
        logger.info("🎉 Инициализация базы данных завершена успешно!")
        return True
    else:
        logger.error("💥 Инициализация завершена с ошибками!")
        return False

def main():
    """Главная функция"""
    logger.info("=" * 50)
    logger.info("🔧 ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ TELEGRAM БОТА")
    logger.info("=" * 50)
    
    success = run_migration()
    
    logger.info("=" * 50)
    if success:
        logger.info("✅ ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
        sys.exit(0)
    else:
        logger.error("❌ ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА С ОШИБКАМИ")
        sys.exit(1)

if __name__ == "__main__":
    main()
