"""
Обработчики стартовых команд и основного меню
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_session
from services.user_service import UserService
from services.analytics_service import AnalyticsService
from utils.keyboards import get_main_menu_keyboard
import logging

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    try:
        user = update.effective_user
        db = get_session()
        
        try:
            user_service = UserService(db)
            analytics_service = AnalyticsService(db)
            
            # Создание или обновление пользователя
            db_user = user_service.create_or_update_user(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            
            # Логирование активности
            analytics_service.log_user_activity(
                user_id=db_user.id,
                activity_type="start_command"
            )
            
            db.commit()
            
            welcome_text = f"""
🤖 Добро пожаловать, {user.first_name}!

Это бот для управления постами с расширенными возможностями:

📝 **Возможности:**
• Создание объектов по шаблонам
• Управление своими объектами
• Просмотр всех объектов
• Встроенная аналитика

👑 **Для администраторов:**
• Управление пользователями
• Модерация объектов
• Расширенная аналитика
• Экспорт данных

Используйте меню ниже для навигации или команду /help для получения справки.
            """
            
            keyboard = get_main_menu_keyboard(db_user.is_admin)
            
            await update.message.reply_text(
                welcome_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в start_command: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при запуске. Попробуйте еще раз."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    try:
        db = get_session()
        
        try:
            user_service = UserService(db)
            db_user = user_service.get_user_by_telegram_id(update.effective_user.id)
            
            if not db_user:
                await update.message.reply_text("❌ Пользователь не найден. Используйте /start")
                return
            
            help_text = """
📚 **Справка по командам:**

**Основные команды:**
/start - Запуск бота и главное меню
/help - Показать эту справку
/profile - Показать профиль пользователя

**Работа с объектами:**
/create_post - Создать новый объект
/my_posts - Мои объекты
/all_posts - Все объекты в системе
/edit_post - Редактировать объект

**Аналитика:**
/analytics - Общая аналитика
/user_stats - Статистика пользователей
/post_stats - Статистика постов
            """
            
            if db_user.is_admin:
                help_text += """
**Административные команды:**
/admin - Панель администратора
/manage_users - Управление пользователями
/manage_posts - Управление постами
/promote_user - Назначить администратора
/export_data - Экспорт данных
                """
            
            help_text += """
**Как использовать:**
1. Создавайте объекты через интерактивные шаблоны
2. Управляйте своими объектами через личный кабинет
3. Просматривайте аналитику и статистику
4. Используйте inline-кнопки для удобной навигации
            """
            
            await update.message.reply_text(help_text, parse_mode='Markdown')
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в help_command: {e}")
        await update.message.reply_text("❌ Ошибка при получении справки.")

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /profile"""
    try:
        db = get_session()
        
        try:
            user_service = UserService(db)
            db_user = user_service.get_user_by_telegram_id(update.effective_user.id)
            
            if not db_user:
                await update.message.reply_text("❌ Пользователь не найден. Используйте /start")
                return
            
            # Получение статистики пользователя
            posts_count = len([p for p in db_user.posts if not p.is_deleted])
            published_posts = len([p for p in db_user.posts if p.is_published and not p.is_deleted])
            
            profile_text = f"""
👤 **Профиль пользователя**

**Основная информация:**
• ID: `{db_user.telegram_id}`
• Имя: {db_user.first_name or 'Не указано'}
• Username: @{db_user.username or 'Не указано'}
• Роль: {'👑 Администратор' if db_user.is_admin else '👤 Пользователь'}

**Статистика:**
• Всего постов: {posts_count}
• Опубликовано: {published_posts}
• Дата регистрации: {db_user.created_at.strftime('%d.%m.%Y %H:%M')}
• Последняя активность: {db_user.last_activity.strftime('%d.%m.%Y %H:%M')}
            """
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📝 Мои посты", callback_data="main_my_posts"),
                    InlineKeyboardButton("📊 Моя статистика", callback_data="main_my_stats")
                ],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
            
            await update.message.reply_text(
                profile_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в profile_command: {e}")
        await update.message.reply_text("❌ Ошибка при получении профиля.")

async def handle_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик callback query для главного меню"""
    try:
        query = update.callback_query
        await query.answer()
        
        data = query.data.replace("main_", "")
        
        if data == "menu":
            db = get_session()
            try:
                user_service = UserService(db)
                db_user = user_service.get_user_by_telegram_id(update.effective_user.id)
                
                keyboard = get_main_menu_keyboard(db_user.is_admin if db_user else False)
                
                await query.edit_message_text(
                    "🏠 **Главное меню**\n\nВыберите действие:",
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            finally:
                db.close()
                
        elif data == "my_posts" or data == "my_objects":
            # Перенаправление на команду просмотра объектов
            from handlers.posts import my_posts_callback
            await my_posts_callback(update, context)
            
        elif data == "my_stats":
            # Перенаправление на персональную статистику
            from handlers.analytics import user_personal_stats_callback
            await user_personal_stats_callback(update, context)
            
    except Exception as e:
        logger.error(f"Ошибка в handle_main_callback: {e}")
        await query.message.reply_text("❌ Ошибка при обработке действия.")
