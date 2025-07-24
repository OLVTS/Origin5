"""
Telegram бот для управления постами с автоматическим созданием БД, системой ролей и встроенной аналитикой
"""

import os
import asyncio
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes

from config import Config
from database import init_database
from handlers import start, posts, admin, analytics

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update.effective_message:
        await update.effective_message.reply_text(
            "❌ Произошла ошибка при обработке команды. Попробуйте еще раз."
        )

def main():
    """Основная функция запуска бота"""
    # Инициализация базы данных
    init_database()
    
    # Создание приложения
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start.start_command))
    application.add_handler(CommandHandler("help", start.help_command))
    application.add_handler(CommandHandler("profile", start.profile_command))
    
    # Обработчики постов
    application.add_handler(CommandHandler("create_post", posts.create_post_command))
    application.add_handler(CommandHandler("my_posts", posts.my_posts_command))
    application.add_handler(CommandHandler("all_posts", posts.all_posts_command))
    application.add_handler(CommandHandler("edit_post", posts.edit_post_command))
    
    # Административные команды
    application.add_handler(CommandHandler("admin", admin.admin_panel_command))
    application.add_handler(CommandHandler("manage_users", admin.manage_users_command))
    application.add_handler(CommandHandler("manage_posts", admin.manage_posts_command))
    application.add_handler(CommandHandler("promote_user", admin.promote_user_command))
    
    # Команды аналитики
    application.add_handler(CommandHandler("analytics", analytics.analytics_command))
    application.add_handler(CommandHandler("user_stats", analytics.user_stats_command))
    application.add_handler(CommandHandler("post_stats", analytics.post_stats_command))
    application.add_handler(CommandHandler("export_data", analytics.export_data_command))
    
    # Обработчики callback query
    application.add_handler(CallbackQueryHandler(posts.handle_post_callback, pattern="^post_"))
    application.add_handler(CallbackQueryHandler(admin.handle_admin_callback, pattern="^admin_"))
    application.add_handler(CallbackQueryHandler(analytics.handle_analytics_callback, pattern="^analytics_"))
    application.add_handler(CallbackQueryHandler(start.handle_main_callback, pattern="^main_"))
    
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, posts.handle_text_message))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запуск бота
    logger.info("Запуск Telegram бота...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
