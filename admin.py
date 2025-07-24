"""
Обработчики административных команд
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_session
from services.user_service import UserService
from services.post_service import PostService
from services.analytics_service import AnalyticsService
from utils.decorators import admin_required
import logging

logger = logging.getLogger(__name__)

@admin_required
async def admin_panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды панели администратора"""
    try:
        db = get_session()
        
        try:
            user_service = UserService(db)
            post_service = PostService(db)
            
            # Получение статистики
            total_users = user_service.get_users_count()
            active_users = user_service.get_active_users_count()
            total_posts = post_service.get_posts_count()
            published_posts = post_service.get_published_posts_count()
            
            text = f"""
👑 **Панель администратора**

📊 **Общая статистика:**
• Всего пользователей: {total_users}
• Активные пользователи: {active_users}
• Всего постов: {total_posts}
• Опубликованных постов: {published_posts}

🛠 **Доступные действия:**
• Управление пользователями
• Модерация постов
• Просмотр аналитики
• Экспорт данных
            """
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👥 Пользователи", callback_data="admin_users"),
                    InlineKeyboardButton("📝 Посты", callback_data="admin_posts")
                ],
                [
                    InlineKeyboardButton("📊 Аналитика", callback_data="admin_analytics"),
                    InlineKeyboardButton("📤 Экспорт", callback_data="admin_export")
                ],
                [
                    InlineKeyboardButton("⚙️ Настройки", callback_data="admin_settings"),
                    InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
                ]
            ])
            
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в admin_panel_command: {e}")
        await update.message.reply_text("❌ Ошибка при загрузке панели администратора.")

@admin_required
async def manage_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды управления пользователями"""
    try:
        db = get_session()
        
        try:
            user_service = UserService(db)
            users = user_service.get_all_users(limit=20)
            
            if not users:
                text = "👥 **Управление пользователями**\n\nПользователи не найдены."
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ])
            else:
                text = "👥 **Управление пользователями**\n\n"
                
                for user in users:
                    status = "👑 Админ" if user.is_admin else "👤 Пользователь"
                    activity_status = "🟢 Активен" if user.is_active else "🔴 Заблокирован"
                    name = user.first_name or user.username or f"ID:{user.telegram_id}"
                    
                    text += f"• {name} ({status}, {activity_status})\n"
                    text += f"  ID: `{user.telegram_id}` | Постов: {len(user.posts)}\n\n"
                
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("👑 Назначить админа", callback_data="admin_promote"),
                        InlineKeyboardButton("🔒 Блокировать", callback_data="admin_block")
                    ],
                    [
                        InlineKeyboardButton("📊 Статистика", callback_data="admin_user_stats"),
                        InlineKeyboardButton("🔄 Обновить", callback_data="admin_users")
                    ],
                    [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
                ])
            
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в manage_users_command: {e}")
        await update.message.reply_text("❌ Ошибка при загрузке пользователей.")

@admin_required
async def manage_posts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды управления постами"""
    try:
        db = get_session()
        
        try:
            post_service = PostService(db)
            
            # Получение последних постов
            recent_posts = post_service.get_recent_posts(limit=10)
            pending_posts = post_service.get_unpublished_posts(limit=10)
            
            text = f"""
📝 **Управление постами**

📊 **Статистика:**
• Всего постов: {post_service.get_posts_count()}
• Опубликованных: {post_service.get_published_posts_count()}
• Ожидают модерации: {len(pending_posts)}

📋 **Последние посты:**
            """
            
            for post in recent_posts[:5]:
                status = "🟢" if post.is_published else "🟡"
                author_name = post.author.first_name or post.author.username or "Аноним"
                text += f"\n• {status} #{post.post_number} - {post.title[:30]}..."
                text += f"\n  👤 {author_name} | 📅 {post.created_at.strftime('%d.%m.%Y')}"
            
            if pending_posts:
                text += f"\n\n⏳ **Ожидают модерации:**"
                for post in pending_posts[:3]:
                    author_name = post.author.first_name or post.author.username or "Аноним"
                    text += f"\n• #{post.post_number} - {post.title[:30]}... ({author_name})"
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📋 Все посты", callback_data="admin_all_posts"),
                    InlineKeyboardButton("⏳ На модерации", callback_data="admin_pending_posts")
                ],
                [
                    InlineKeyboardButton("🗑 Удаленные", callback_data="admin_deleted_posts"),
                    InlineKeyboardButton("📊 Статистика", callback_data="admin_post_stats")
                ],
                [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
            ])
            
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в manage_posts_command: {e}")
        await update.message.reply_text("❌ Ошибка при загрузке постов.")

@admin_required
async def promote_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды назначения администратора"""
    try:
        args = context.args
        if not args:
            await update.message.reply_text(
                "❌ Укажите Telegram ID пользователя для назначения администратором.\n\n"
                "Пример: /promote_user 123456789"
            )
            return
        
        try:
            target_telegram_id = int(args[0])
        except ValueError:
            await update.message.reply_text("❌ ID пользователя должен быть числом.")
            return
        
        db = get_session()
        
        try:
            user_service = UserService(db)
            analytics_service = AnalyticsService(db)
            
            # Получение администратора
            admin_user = user_service.get_user_by_telegram_id(update.effective_user.id)
            
            # Получение целевого пользователя
            target_user = user_service.get_user_by_telegram_id(target_telegram_id)
            
            if not target_user:
                await update.message.reply_text(
                    f"❌ Пользователь с ID {target_telegram_id} не найден.\n\n"
                    "Пользователь должен сначала запустить бота командой /start"
                )
                return
            
            if target_user.is_admin:
                await update.message.reply_text(
                    f"ℹ️ Пользователь {target_user.first_name or target_user.username} уже является администратором."
                )
                return
            
            # Назначение администратором
            success = user_service.promote_to_admin(target_telegram_id)
            
            if success:
                # Логирование активности
                analytics_service.log_user_activity(
                    user_id=admin_user.id,
                    activity_type="user_promote",
                    activity_data={"target_user_id": target_user.id}
                )
                
                db.commit()
                
                target_name = target_user.first_name or target_user.username or f"ID:{target_telegram_id}"
                
                await update.message.reply_text(
                    f"✅ Пользователь {target_name} успешно назначен администратором!"
                )
                
                # Уведомление пользователю (если возможно)
                try:
                    await context.bot.send_message(
                        chat_id=target_telegram_id,
                        text="🎉 Поздравляем! Вы были назначены администратором бота.\n\n"
                             "Теперь вам доступны расширенные возможности управления."
                    )
                except Exception:
                    # Не удалось отправить уведомление (пользователь заблокировал бота и т.д.)
                    pass
                
            else:
                await update.message.reply_text("❌ Ошибка при назначении администратора.")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в promote_user_command: {e}")
        await update.message.reply_text("❌ Ошибка при назначении администратора.")

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик callback query для административных действий"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Проверка прав администратора
        db = get_session()
        try:
            user_service = UserService(db)
            db_user = user_service.get_user_by_telegram_id(update.effective_user.id)
            
            if not db_user or not db_user.is_admin:
                await query.edit_message_text("❌ Недостаточно прав для выполнения этого действия.")
                return
        finally:
            db.close()
        
        data = query.data.replace("admin_", "")
        
        if data == "panel":
            await show_admin_panel(update, context)
            
        elif data == "users":
            await show_users_management(update, context)
            
        elif data == "posts":
            await show_posts_management(update, context)
            
        elif data == "analytics":
            # Перенаправление на расширенную аналитику
            from handlers.analytics import show_admin_analytics
            await show_admin_analytics(update, context)
            
        elif data == "export":
            await show_export_options(update, context)
            
        elif data == "settings":
            await show_admin_settings(update, context)
            
        elif data.startswith("user_"):
            await handle_user_action(update, context, data)
            
        elif data.startswith("post_"):
            await handle_post_action(update, context, data)
            
    except Exception as e:
        logger.error(f"Ошибка в handle_admin_callback: {e}")
        await query.message.reply_text("❌ Ошибка при обработке административного действия.")

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ панели администратора"""
    try:
        db = get_session()
        
        try:
            user_service = UserService(db)
            post_service = PostService(db)
            
            # Получение статистики
            total_users = user_service.get_users_count()
            active_users = user_service.get_active_users_count()
            total_posts = post_service.get_posts_count()
            published_posts = post_service.get_published_posts_count()
            
            text = f"""
👑 **Панель администратора**

📊 **Общая статистика:**
• Всего пользователей: {total_users}
• Активные пользователи: {active_users}
• Всего постов: {total_posts}
• Опубликованных постов: {published_posts}

🛠 **Доступные действия:**
• Управление пользователями
• Модерация постов
• Просмотр аналитики
• Экспорт данных
            """
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👥 Пользователи", callback_data="admin_users"),
                    InlineKeyboardButton("📝 Посты", callback_data="admin_posts")
                ],
                [
                    InlineKeyboardButton("📊 Аналитика", callback_data="admin_analytics"),
                    InlineKeyboardButton("📤 Экспорт", callback_data="admin_export")
                ],
                [
                    InlineKeyboardButton("⚙️ Настройки", callback_data="admin_settings"),
                    InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
                ]
            ])
            
            await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в show_admin_panel: {e}")

async def show_users_management(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ управления пользователями"""
    try:
        db = get_session()
        
        try:
            user_service = UserService(db)
            users = user_service.get_all_users(limit=20)
            
            text = "👥 **Управление пользователями**\n\n"
            
            if not users:
                text += "Пользователи не найдены."
            else:
                for user in users:
                    status = "👑 Админ" if user.is_admin else "👤 Пользователь"
                    activity_status = "🟢 Активен" if user.is_active else "🔴 Заблокирован"
                    name = user.first_name or user.username or f"ID:{user.telegram_id}"
                    
                    text += f"• {name} ({status}, {activity_status})\n"
                    text += f"  ID: `{user.telegram_id}` | Постов: {len(user.posts)}\n\n"
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👑 Назначить админа", callback_data="admin_promote"),
                    InlineKeyboardButton("🔒 Блокировать", callback_data="admin_block")
                ],
                [
                    InlineKeyboardButton("📊 Статистика", callback_data="admin_user_stats"),
                    InlineKeyboardButton("🔄 Обновить", callback_data="admin_users")
                ],
                [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
            ])
            
            await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в show_users_management: {e}")

async def show_posts_management(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ управления постами"""
    try:
        db = get_session()
        
        try:
            post_service = PostService(db)
            
            # Получение статистики и постов
            recent_posts = post_service.get_recent_posts(limit=10)
            pending_posts = post_service.get_unpublished_posts(limit=10)
            
            text = f"""
📝 **Управление постами**

📊 **Статистика:**
• Всего постов: {post_service.get_posts_count()}
• Опубликованных: {post_service.get_published_posts_count()}
• Ожидают модерации: {len(pending_posts)}

📋 **Последние посты:**
            """
            
            for post in recent_posts[:5]:
                status = "🟢" if post.is_published else "🟡"
                author_name = post.author.first_name or post.author.username or "Аноним"
                text += f"\n• {status} #{post.post_number} - {post.title[:30]}..."
                text += f"\n  👤 {author_name} | 📅 {post.created_at.strftime('%d.%m.%Y')}"
            
            if pending_posts:
                text += f"\n\n⏳ **Ожидают модерации:**"
                for post in pending_posts[:3]:
                    author_name = post.author.first_name or post.author.username or "Аноним"
                    text += f"\n• #{post.post_number} - {post.title[:30]}... ({author_name})"
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📋 Все посты", callback_data="admin_all_posts"),
                    InlineKeyboardButton("⏳ На модерации", callback_data="admin_pending_posts")
                ],
                [
                    InlineKeyboardButton("🗑 Удаленные", callback_data="admin_deleted_posts"),
                    InlineKeyboardButton("📊 Статистика", callback_data="admin_post_stats")
                ],
                [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
            ])
            
            await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в show_posts_management: {e}")

async def show_export_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ опций экспорта данных"""
    try:
        text = """
📤 **Экспорт данных**

Выберите тип данных для экспорта:

📊 **Доступные форматы:**
• CSV - для анализа в Excel/Google Sheets
• JSON - для программной обработки
• PDF - для отчетов

🗂 **Типы данных:**
• Пользователи и их активность
• Посты и статистика публикаций
• Аналитика и метрики
• Полный дамп данных
        """
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👥 Пользователи (CSV)", callback_data="admin_export_users_csv"),
                InlineKeyboardButton("📝 Посты (CSV)", callback_data="admin_export_posts_csv")
            ],
            [
                InlineKeyboardButton("📊 Аналитика (JSON)", callback_data="admin_export_analytics_json"),
                InlineKeyboardButton("📋 Полный дамп", callback_data="admin_export_full")
            ],
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
        ])
        
        await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в show_export_options: {e}")

async def show_admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ настроек администратора"""
    try:
        text = """
⚙️ **Настройки системы**

🔧 **Доступные настройки:**
• Управление шаблонами постов
• Настройки автоматической модерации
• Конфигурация уведомлений
• Параметры аналитики
• Настройки резервного копирования

📝 **Шаблоны постов:**
• Добавление новых шаблонов
• Редактирование существующих
• Управление полями шаблонов

⏰ **Автоматизация:**
• Автопубликация постов
• Уведомления о новых постах
• Еженедельные отчеты
        """
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📋 Шаблоны", callback_data="admin_templates"),
                InlineKeyboardButton("🔔 Уведомления", callback_data="admin_notifications")
            ],
            [
                InlineKeyboardButton("⏰ Автоматизация", callback_data="admin_automation"),
                InlineKeyboardButton("💾 Резервные копии", callback_data="admin_backups")
            ],
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
        ])
        
        await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в show_admin_settings: {e}")
