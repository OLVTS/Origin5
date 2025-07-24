"""
Обработчики команд аналитики и статистики
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_session
from services.analytics_service import AnalyticsService
from services.user_service import UserService
from services.post_service import PostService
from utils.decorators import admin_required
import logging
import io
import matplotlib
matplotlib.use('Agg')  # Для работы без GUI
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

async def analytics_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды общей аналитики"""
    try:
        db = get_session()
        
        try:
            user_service = UserService(db)
            analytics_service = AnalyticsService(db)
            
            db_user = user_service.get_user_by_telegram_id(update.effective_user.id)
            
            if not db_user:
                await update.message.reply_text("❌ Пользователь не найден. Используйте /start")
                return
            
            # Получение базовой аналитики
            analytics_data = analytics_service.get_basic_analytics()
            
            text = f"""
📊 **Аналитика системы**

📈 **Общие показатели:**
• Всего пользователей: {analytics_data['total_users']}
• Активных за неделю: {analytics_data['weekly_active_users']}
• Всего постов: {analytics_data['total_posts']}
• Опубликованных постов: {analytics_data['published_posts']}

📅 **За последние 7 дней:**
• Новые пользователи: {analytics_data['new_users_week']}
• Созданные посты: {analytics_data['new_posts_week']}
• Активность пользователей: {analytics_data['user_activities_week']}

📋 **Популярные шаблоны:**
            """
            
            # Добавление информации о популярных шаблонах
            popular_templates = analytics_service.get_popular_templates()
            for template in popular_templates[:3]:
                text += f"\n• {template['name']}: {template['usage_count']} использований"
            
            keyboard_buttons = [
                [
                    InlineKeyboardButton("👤 Моя статистика", callback_data="analytics_personal"),
                    InlineKeyboardButton("📈 Графики", callback_data="analytics_charts")
                ]
            ]
            
            if db_user.is_admin:
                keyboard_buttons.extend([
                    [
                        InlineKeyboardButton("👥 Статистика пользователей", callback_data="analytics_users"),
                        InlineKeyboardButton("📝 Статистика постов", callback_data="analytics_posts")
                    ],
                    [
                        InlineKeyboardButton("📊 Расширенная аналитика", callback_data="analytics_advanced"),
                        InlineKeyboardButton("📤 Экспорт данных", callback_data="analytics_export")
                    ]
                ])
            
            keyboard_buttons.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
            
            keyboard = InlineKeyboardMarkup(keyboard_buttons)
            
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в analytics_command: {e}")
        await update.message.reply_text("❌ Ошибка при получении аналитики.")

async def user_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды статистики пользователей"""
    try:
        db = get_session()
        
        try:
            user_service = UserService(db)
            analytics_service = AnalyticsService(db)
            
            db_user = user_service.get_user_by_telegram_id(update.effective_user.id)
            
            if not db_user:
                await update.message.reply_text("❌ Пользователь не найден. Используйте /start")
                return
            
            # Получение статистики пользователя
            user_stats = analytics_service.get_user_statistics(db_user.id)
            
            text = f"""
👤 **Ваша статистика**

📊 **Активность:**
• Всего действий: {user_stats['total_activities']}
• Действий за неделю: {user_stats['weekly_activities']}
• Последняя активность: {db_user.last_activity.strftime('%d.%m.%Y %H:%M')}

📝 **Посты:**
• Всего создано: {user_stats['total_posts']}
• Опубликовано: {user_stats['published_posts']}
• Черновиков: {user_stats['draft_posts']}

📈 **Популярность:**
• Просмотры постов: {user_stats.get('post_views', 0)}
• Использованные шаблоны: {len(user_stats.get('used_templates', []))}

⏰ **Временные показатели:**
• Среднее время создания поста: {user_stats.get('avg_post_creation_time', 'N/A')}
• Наиболее активный день: {user_stats.get('most_active_day', 'N/A')}
            """
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📈 Графики активности", callback_data="analytics_personal_charts"),
                    InlineKeyboardButton("📋 Детальная статистика", callback_data="analytics_personal_detailed")
                ],
                [
                    InlineKeyboardButton("📊 Общая аналитика", callback_data="analytics_general"),
                    InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
                ]
            ])
            
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в user_stats_command: {e}")
        await update.message.reply_text("❌ Ошибка при получении статистики.")

@admin_required
async def post_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды статистики постов (только для админов)"""
    try:
        db = get_session()
        
        try:
            analytics_service = AnalyticsService(db)
            post_service = PostService(db)
            
            # Получение статистики постов
            post_stats = analytics_service.get_post_statistics()
            
            text = f"""
📝 **Статистика постов**

📊 **Общие показатели:**
• Всего постов: {post_stats['total_posts']}
• Опубликованных: {post_stats['published_posts']}
• Черновиков: {post_stats['draft_posts']}
• Удаленных: {post_stats['deleted_posts']}

📈 **Динамика:**
• Постов за неделю: {post_stats['posts_this_week']}
• Постов за месяц: {post_stats['posts_this_month']}
• Среднее в день: {post_stats['avg_posts_per_day']:.1f}

📋 **По шаблонам:**
            """
            
            # Добавление статистики по шаблонам
            template_stats = analytics_service.get_template_usage_stats()
            for template_stat in template_stats[:5]:
                text += f"\n• {template_stat['template_name']}: {template_stat['usage_count']} постов"
            
            text += f"""

👤 **По авторам:**
• Самый активный автор: {post_stats.get('most_active_author', 'N/A')}
• Средняя длина поста: {post_stats.get('avg_post_length', 0)} символов
• Самый популярный пост: #{post_stats.get('most_popular_post', 'N/A')}
            """
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📈 Графики постов", callback_data="analytics_post_charts"),
                    InlineKeyboardButton("👥 По авторам", callback_data="analytics_authors")
                ],
                [
                    InlineKeyboardButton("📋 Детальный отчет", callback_data="analytics_post_detailed"),
                    InlineKeyboardButton("📤 Экспорт", callback_data="analytics_export_posts")
                ],
                [InlineKeyboardButton("🔙 Назад", callback_data="analytics_general")]
            ])
            
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в post_stats_command: {e}")
        await update.message.reply_text("❌ Ошибка при получении статистики постов.")

@admin_required
async def export_data_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды экспорта данных (только для админов)"""
    try:
        text = """
📤 **Экспорт данных**

Выберите тип данных для экспорта:

📊 **Доступные форматы:**
• CSV - для анализа в Excel/Google Sheets
• JSON - для программной обработки
• PDF - для отчетов

🗂 **Типы данных:**
• Аналитика и метрики
• Пользователи и активность
• Посты и статистика
• Полный дамп системы

⚠️ **Примечание:** Экспорт может занять некоторое время для больших объемов данных.
        """
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📊 Аналитика (CSV)", callback_data="analytics_export_analytics_csv"),
                InlineKeyboardButton("👥 Пользователи (CSV)", callback_data="analytics_export_users_csv")
            ],
            [
                InlineKeyboardButton("📝 Посты (JSON)", callback_data="analytics_export_posts_json"),
                InlineKeyboardButton("📋 Полный дамп", callback_data="analytics_export_full")
            ],
            [
                InlineKeyboardButton("📈 Отчет (PDF)", callback_data="analytics_export_report_pdf"),
                InlineKeyboardButton("🔙 Назад", callback_data="analytics_general")
            ]
        ])
        
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в export_data_command: {e}")
        await update.message.reply_text("❌ Ошибка при подготовке экспорта.")

async def handle_analytics_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик callback query для аналитики"""
    try:
        query = update.callback_query
        await query.answer()
        
        data = query.data.replace("analytics_", "")
        
        if data == "general":
            await show_general_analytics(update, context)
            
        elif data == "personal":
            await user_personal_stats_callback(update, context)
            
        elif data == "charts":
            await generate_analytics_charts(update, context)
            
        elif data == "users":
            await show_user_analytics(update, context)
            
        elif data == "posts":
            await show_post_analytics(update, context)
            
        elif data == "advanced":
            await show_advanced_analytics(update, context)
            
        elif data.startswith("export_"):
            await handle_export_request(update, context, data.replace("export_", ""))
            
        elif data == "personal_charts":
            await generate_personal_charts(update, context)
            
        elif data == "personal_detailed":
            await show_detailed_personal_stats(update, context)
            
        elif data == "post_charts":
            await generate_post_charts(update, context)
            
        elif data == "authors":
            await show_author_analytics(update, context)
            
    except Exception as e:
        logger.error(f"Ошибка в handle_analytics_callback: {e}")
        await query.message.reply_text("❌ Ошибка при обработке аналитики.")

async def show_general_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ общей аналитики"""
    try:
        db = get_session()
        
        try:
            analytics_service = AnalyticsService(db)
            analytics_data = analytics_service.get_basic_analytics()
            
            text = f"""
📊 **Общая аналитика системы**

📈 **Основные метрики:**
• Всего пользователей: {analytics_data['total_users']}
• Активных за неделю: {analytics_data['weekly_active_users']}
• Всего постов: {analytics_data['total_posts']}
• Опубликованных: {analytics_data['published_posts']}

📅 **Динамика (7 дней):**
• Новые пользователи: {analytics_data['new_users_week']}
• Новые посты: {analytics_data['new_posts_week']}
• Активности: {analytics_data['user_activities_week']}

🎯 **Эффективность:**
• Конверсия в публикацию: {analytics_data.get('publication_rate', 0):.1f}%
• Среднее постов на пользователя: {analytics_data.get('avg_posts_per_user', 0):.1f}
• Активность пользователей: {analytics_data.get('user_activity_rate', 0):.1f}%
            """
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📈 Графики", callback_data="analytics_charts"),
                    InlineKeyboardButton("👥 Пользователи", callback_data="analytics_users")
                ],
                [
                    InlineKeyboardButton("📝 Посты", callback_data="analytics_posts"),
                    InlineKeyboardButton("🔧 Расширенная", callback_data="analytics_advanced")
                ],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
            
            await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в show_general_analytics: {e}")

async def user_personal_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback для персональной статистики пользователя"""
    try:
        db = get_session()
        
        try:
            user_service = UserService(db)
            analytics_service = AnalyticsService(db)
            
            db_user = user_service.get_user_by_telegram_id(update.effective_user.id)
            
            if not db_user:
                await update.callback_query.edit_message_text("❌ Пользователь не найден.")
                return
            
            # Получение детальной статистики пользователя
            user_stats = analytics_service.get_detailed_user_statistics(db_user.id)
            
            text = f"""
👤 **Ваша персональная статистика**

📊 **Основные показатели:**
• Дней в системе: {user_stats['days_since_registration']}
• Всего действий: {user_stats['total_activities']}
• Создано постов: {user_stats['total_posts']}
• Опубликовано: {user_stats['published_posts']}

📈 **Активность:**
• Действий за неделю: {user_stats['weekly_activities']}
• Действий за месяц: {user_stats['monthly_activities']}
• Средняя активность в день: {user_stats['avg_daily_activities']:.1f}

📝 **Контент:**
• Черновиков: {user_stats['draft_posts']}
• Среднее время создания: {user_stats.get('avg_creation_time', 'N/A')}
• Любимый шаблон: {user_stats.get('favorite_template', 'N/A')}

🏆 **Достижения:**
• Ранг активности: {user_stats.get('activity_rank', 'N/A')}
• Процентиль публикаций: {user_stats.get('publication_percentile', 0):.1f}%
            """
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📈 Мои графики", callback_data="analytics_personal_charts"),
                    InlineKeyboardButton("📋 Детали", callback_data="analytics_personal_detailed")
                ],
                [
                    InlineKeyboardButton("📊 Общая аналитика", callback_data="analytics_general"),
                    InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
                ]
            ])
            
            await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в user_personal_stats_callback: {e}")

async def generate_analytics_charts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Генерация графиков общей аналитики"""
    try:
        await update.callback_query.answer("📈 Генерация графиков...")
        
        db = get_session()
        
        try:
            analytics_service = AnalyticsService(db)
            
            # Получение данных для графиков
            daily_stats = analytics_service.get_daily_statistics(days=30)
            
            # Создание графика активности пользователей
            plt.figure(figsize=(12, 8))
            
            # График 1: Активность пользователей
            plt.subplot(2, 2, 1)
            dates = [stat['date'] for stat in daily_stats]
            user_activities = [stat['user_activities'] for stat in daily_stats]
            
            plt.plot(dates, user_activities, marker='o', color='#2E86AB')
            plt.title('Активность пользователей (30 дней)')
            plt.xlabel('Дата')
            plt.ylabel('Количество действий')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            # График 2: Создание постов
            plt.subplot(2, 2, 2)
            post_creations = [stat['posts_created'] for stat in daily_stats]
            
            plt.bar(dates, post_creations, color='#A23B72', alpha=0.7)
            plt.title('Создание постов (30 дней)')
            plt.xlabel('Дата')
            plt.ylabel('Количество постов')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            # График 3: Новые пользователи
            plt.subplot(2, 2, 3)
            new_users = [stat['new_users'] for stat in daily_stats]
            
            plt.plot(dates, new_users, marker='s', color='#F18F01', linewidth=2)
            plt.title('Новые пользователи (30 дней)')
            plt.xlabel('Дата')
            plt.ylabel('Количество пользователей')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            # График 4: Использование шаблонов
            plt.subplot(2, 2, 4)
            template_stats = analytics_service.get_template_usage_stats()
            
            template_names = [stat['template_name'] for stat in template_stats[:5]]
            usage_counts = [stat['usage_count'] for stat in template_stats[:5]]
            
            plt.pie(usage_counts, labels=template_names, autopct='%1.1f%%', startangle=90)
            plt.title('Использование шаблонов')
            
            plt.tight_layout()
            
            # Сохранение графика в буфер
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            
            # Отправка графика
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=buf,
                caption="📈 **Графики общей аналитики системы**\n\nАнализ активности за последние 30 дней",
                parse_mode='Markdown'
            )
            
            plt.close()
            buf.close()
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в generate_analytics_charts: {e}")
        await update.callback_query.message.reply_text("❌ Ошибка при генерации графиков.")

async def show_admin_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ расширенной аналитики для администраторов"""
    try:
        # Проверка прав администратора
        db = get_session()
        try:
            user_service = UserService(db)
            db_user = user_service.get_user_by_telegram_id(update.effective_user.id)
            
            if not db_user or not db_user.is_admin:
                await update.callback_query.edit_message_text("❌ Недостаточно прав.")
                return
            
            analytics_service = AnalyticsService(db)
            admin_analytics = analytics_service.get_admin_analytics()
            
            text = f"""
👑 **Расширенная аналитика (Админ)**

🎯 **Ключевые метрики:**
• DAU (дневные активные): {admin_analytics['daily_active_users']}
• WAU (недельные активные): {admin_analytics['weekly_active_users']}
• MAU (месячные активные): {admin_analytics['monthly_active_users']}
• Retention Rate: {admin_analytics['retention_rate']:.1f}%

📊 **Конверсии:**
• Регистрация → Первый пост: {admin_analytics['first_post_conversion']:.1f}%
• Черновик → Публикация: {admin_analytics['publication_conversion']:.1f}%
• Активность пользователей: {admin_analytics['user_engagement']:.1f}%

⚡ **Производительность:**
• Среднее время создания поста: {admin_analytics['avg_post_creation_time']}
• Пик активности: {admin_analytics['peak_activity_hour']}:00
• Самый продуктивный день: {admin_analytics['most_productive_day']}

🔥 **Тренды:**
• Рост пользователей: {admin_analytics['user_growth_rate']:+.1f}%
• Рост постов: {admin_analytics['post_growth_rate']:+.1f}%
• Изменение активности: {admin_analytics['activity_change']:+.1f}%
            """
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📈 Детальные графики", callback_data="analytics_admin_charts"),
                    InlineKeyboardButton("👥 Анализ пользователей", callback_data="analytics_user_analysis")
                ],
                [
                    InlineKeyboardButton("📝 Анализ контента", callback_data="analytics_content_analysis"),
                    InlineKeyboardButton("🔍 Поведенческий анализ", callback_data="analytics_behavior")
                ],
                [
                    InlineKeyboardButton("📤 Экспорт отчета", callback_data="analytics_export_admin_report"),
                    InlineKeyboardButton("🔙 Назад", callback_data="analytics_general")
                ]
            ])
            
            await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в show_admin_analytics: {e}")

async def handle_export_request(update: Update, context: ContextTypes.DEFAULT_TYPE, export_type: str) -> None:
    """Обработка запроса на экспорт данных"""
    try:
        await update.callback_query.answer("📤 Подготовка экспорта...")
        
        db = get_session()
        
        try:
            analytics_service = AnalyticsService(db)
            
            if export_type == "analytics_csv":
                # Экспорт аналитики в CSV
                analytics_data = analytics_service.get_daily_statistics(days=365)
                df = pd.DataFrame(analytics_data)
                
                # Создание CSV в буфер
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False, encoding='utf-8')
                csv_buffer.seek(0)
                
                # Конвертация в байты для отправки
                csv_bytes = io.BytesIO(csv_buffer.getvalue().encode('utf-8'))
                csv_bytes.name = f"analytics_{datetime.now().strftime('%Y%m%d')}.csv"
                
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=csv_bytes,
                    caption="📊 Экспорт аналитики в формате CSV",
                    filename=f"analytics_{datetime.now().strftime('%Y%m%d')}.csv"
                )
                
            elif export_type == "users_csv":
                # Экспорт пользователей в CSV
                user_service = UserService(db)
                users_data = analytics_service.export_users_data()
                df = pd.DataFrame(users_data)
                
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False, encoding='utf-8')
                csv_buffer.seek(0)
                
                csv_bytes = io.BytesIO(csv_buffer.getvalue().encode('utf-8'))
                csv_bytes.name = f"users_{datetime.now().strftime('%Y%m%d')}.csv"
                
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=csv_bytes,
                    caption="👥 Экспорт данных пользователей в формате CSV",
                    filename=f"users_{datetime.now().strftime('%Y%m%d')}.csv"
                )
                
            elif export_type == "posts_json":
                # Экспорт постов в JSON
                posts_data = analytics_service.export_posts_data()
                
                import json
                json_str = json.dumps(posts_data, ensure_ascii=False, indent=2, default=str)
                json_bytes = io.BytesIO(json_str.encode('utf-8'))
                json_bytes.name = f"posts_{datetime.now().strftime('%Y%m%d')}.json"
                
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=json_bytes,
                    caption="📝 Экспорт данных постов в формате JSON",
                    filename=f"posts_{datetime.now().strftime('%Y%m%d')}.json"
                )
                
            else:
                await update.callback_query.message.reply_text("❌ Неизвестный тип экспорта.")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в handle_export_request: {e}")
        await update.callback_query.message.reply_text("❌ Ошибка при экспорте данных.")
