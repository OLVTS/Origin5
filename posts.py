"""
Обработчики команд для работы с постами
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_session
from services.post_service import PostService
from services.user_service import UserService
from services.analytics_service import AnalyticsService
from utils.templates import get_post_templates, get_template_fields
from utils.keyboards import get_posts_keyboard, get_post_actions_keyboard
import logging

logger = logging.getLogger(__name__)

# Состояния для создания поста
user_states = {}

async def create_post_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды создания поста"""
    try:
        db = get_session()
        
        try:
            user_service = UserService(db)
            db_user = user_service.get_user_by_telegram_id(update.effective_user.id)
            
            if not db_user:
                await update.message.reply_text("❌ Пользователь не найден. Используйте /start")
                return
            
            # Получение доступных шаблонов
            templates = get_post_templates()
            
            if not templates:
                await update.message.reply_text("❌ Шаблоны постов недоступны.")
                return
            
            # Создание клавиатуры с шаблонами
            keyboard_buttons = []
            for template in templates:
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        f"📋 {template['name']}", 
                        callback_data=f"post_template_{template['id']}"
                    )
                ])
            
            keyboard_buttons.append([
                InlineKeyboardButton("❌ Отмена", callback_data="post_cancel")
            ])
            
            keyboard = InlineKeyboardMarkup(keyboard_buttons)
            
            text = """
📝 **Создание нового поста**

Выберите шаблон для создания поста:

📋 **Доступные шаблоны:**
• Новость - для новостных сообщений
• Статья - для развернутых статей
• Объявление - для важных объявлений
• Обзор - для обзоров и рецензий
            """
            
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в create_post_command: {e}")
        await update.message.reply_text("❌ Ошибка при создании поста.")

async def my_posts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды просмотра своих постов"""
    try:
        await my_posts_callback(update, context, is_command=True)
    except Exception as e:
        logger.error(f"Ошибка в my_posts_command: {e}")
        await update.message.reply_text("❌ Ошибка при получении постов.")

async def my_posts_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, is_command=False) -> None:
    """Обработчик просмотра своих постов (callback и команда)"""
    try:
        db = get_session()
        
        try:
            user_service = UserService(db)
            post_service = PostService(db)
            
            db_user = user_service.get_user_by_telegram_id(update.effective_user.id)
            
            if not db_user:
                message_text = "❌ Пользователь не найден. Используйте /start"
                if is_command:
                    await update.message.reply_text(message_text)
                else:
                    await update.callback_query.edit_message_text(message_text)
                return
            
            # Получение постов пользователя
            posts = post_service.get_user_posts(db_user.id)
            
            if not posts:
                text = "📝 **Мои посты**\n\nУ вас пока нет созданных постов.\n\nИспользуйте /create_post для создания первого поста."
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Создать пост", callback_data="post_create")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ])
            else:
                active_posts = [p for p in posts if not p.is_deleted]
                published_posts = [p for p in active_posts if p.is_published]
                
                text = f"""
📝 **Мои посты**

📊 **Статистика:**
• Всего постов: {len(active_posts)}
• Опубликовано: {len(published_posts)}
• Черновиков: {len(active_posts) - len(published_posts)}

📋 **Последние посты:**
                """
                
                # Показываем последние 5 постов
                for post in active_posts[:5]:
                    status = "🟢 Опубликован" if post.is_published else "🟡 Черновик"
                    text += f"\n• #{post.post_number} - {post.title[:30]}... ({status})"
                
                keyboard_buttons = [
                    [InlineKeyboardButton("📋 Все мои посты", callback_data="post_list_my")],
                    [InlineKeyboardButton("➕ Создать пост", callback_data="post_create")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ]
                keyboard = InlineKeyboardMarkup(keyboard_buttons)
            
            if is_command:
                await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
            else:
                await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в my_posts_callback: {e}")

async def all_posts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды просмотра всех постов"""
    try:
        db = get_session()
        
        try:
            user_service = UserService(db)
            post_service = PostService(db)
            
            db_user = user_service.get_user_by_telegram_id(update.effective_user.id)
            
            if not db_user:
                await update.message.reply_text("❌ Пользователь не найден. Используйте /start")
                return
            
            # Получение всех опубликованных постов
            posts = post_service.get_published_posts(limit=20)
            
            if not posts:
                text = "📰 **Все посты**\n\nПостов пока нет.\n\nСтаньте первым, кто создаст пост!"
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Создать пост", callback_data="post_create")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ])
            else:
                text = f"📰 **Все посты** (последние {len(posts)})\n\n"
                
                for post in posts:
                    author_name = post.author.first_name or post.author.username or "Аноним"
                    text += f"• #{post.post_number} - {post.title[:40]}...\n"
                    text += f"  👤 {author_name} | 📅 {post.published_at.strftime('%d.%m.%Y')}\n\n"
                
                keyboard_buttons = [
                    [InlineKeyboardButton("📋 Подробный список", callback_data="post_list_all")],
                    [InlineKeyboardButton("🔍 Поиск постов", callback_data="post_search")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ]
                keyboard = InlineKeyboardMarkup(keyboard_buttons)
            
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в all_posts_command: {e}")
        await update.message.reply_text("❌ Ошибка при получении постов.")

async def edit_post_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды редактирования поста"""
    try:
        args = context.args
        if not args:
            await update.message.reply_text(
                "❌ Укажите номер поста для редактирования.\n\nПример: /edit_post 123"
            )
            return
        
        try:
            post_number = int(args[0])
        except ValueError:
            await update.message.reply_text("❌ Номер поста должен быть числом.")
            return
        
        db = get_session()
        
        try:
            user_service = UserService(db)
            post_service = PostService(db)
            
            db_user = user_service.get_user_by_telegram_id(update.effective_user.id)
            
            if not db_user:
                await update.message.reply_text("❌ Пользователь не найден. Используйте /start")
                return
            
            # Получение поста
            post = post_service.get_post_by_number(post_number)
            
            if not post:
                await update.message.reply_text(f"❌ Пост #{post_number} не найден.")
                return
            
            # Проверка прав доступа
            if post.author_id != db_user.id and not db_user.is_admin:
                await update.message.reply_text("❌ Вы можете редактировать только свои посты.")
                return
            
            # Показ информации о посте и возможности редактирования
            status = "🟢 Опубликован" if post.is_published else "🟡 Черновик"
            text = f"""
✏️ **Редактирование поста #{post.post_number}**

📋 **Текущая информация:**
• Заголовок: {post.title}
• Статус: {status}
• Автор: {post.author.first_name or post.author.username}
• Создан: {post.created_at.strftime('%d.%m.%Y %H:%M')}
• Обновлен: {post.updated_at.strftime('%d.%m.%Y %H:%M')}

**Содержание:**
{post.content[:200]}{'...' if len(post.content) > 200 else ''}
            """
            
            keyboard = get_post_actions_keyboard(post, db_user.is_admin)
            
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в edit_post_command: {e}")
        await update.message.reply_text("❌ Ошибка при редактировании поста.")

async def handle_post_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик callback query для постов"""
    try:
        query = update.callback_query
        await query.answer()
        
        data = query.data.replace("post_", "")
        
        if data.startswith("template_"):
            template_id = data.replace("template_", "")
            await handle_template_selection(update, context, template_id)
            
        elif data == "create":
            # Перенаправление на создание поста
            await create_post_command(update, context)
            
        elif data == "cancel":
            # Отмена создания поста
            if update.effective_user.id in user_states:
                del user_states[update.effective_user.id]
            
            await query.edit_message_text(
                "❌ Создание поста отменено.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ])
            )
            
        elif data.startswith("view_"):
            post_number = int(data.replace("view_", ""))
            await show_post_details(update, context, post_number)
            
        elif data.startswith("edit_"):
            post_number = int(data.replace("edit_", ""))
            await start_post_editing(update, context, post_number)
            
        elif data.startswith("delete_"):
            post_number = int(data.replace("delete_", ""))
            await confirm_post_deletion(update, context, post_number)
            
        elif data.startswith("publish_"):
            post_number = int(data.replace("publish_", ""))
            await toggle_post_publication(update, context, post_number)
            
    except Exception as e:
        logger.error(f"Ошибка в handle_post_callback: {e}")
        await query.message.reply_text("❌ Ошибка при обработке действия.")

async def handle_template_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, template_id: str) -> None:
    """Обработка выбора шаблона для поста"""
    try:
        templates = get_post_templates()
        template = next((t for t in templates if t['id'] == template_id), None)
        
        if not template:
            await update.callback_query.edit_message_text("❌ Шаблон не найден.")
            return
        
        # Инициализация состояния пользователя
        user_states[update.effective_user.id] = {
            'state': 'creating_post',
            'template': template,
            'fields': {},
            'current_field': 0
        }
        
        # Начинаем заполнение первого поля
        await ask_next_field(update, context)
        
    except Exception as e:
        logger.error(f"Ошибка в handle_template_selection: {e}")

async def ask_next_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Запрос следующего поля шаблона"""
    try:
        user_id = update.effective_user.id
        if user_id not in user_states:
            return
        
        state = user_states[user_id]
        template = state['template']
        fields = get_template_fields(template['id'])
        current_field_index = state['current_field']
        
        if current_field_index >= len(fields):
            # Все поля заполнены, создаем пост
            await create_post_from_template(update, context)
            return
        
        field = fields[current_field_index]
        
        text = f"""
📝 **Создание поста: {template['name']}**

Шаг {current_field_index + 1} из {len(fields)}

**{field['label']}**
{field.get('description', '')}

{field.get('placeholder', 'Введите значение:')}
        """
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Отмена", callback_data="post_cancel")]
        ])
        
        await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в ask_next_field: {e}")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    try:
        user_id = update.effective_user.id
        
        if user_id in user_states and user_states[user_id]['state'] == 'creating_post':
            await process_field_input(update, context)
        else:
            # Обычное сообщение, можно добавить общий ответ
            await update.message.reply_text(
                "👋 Привет! Используйте команды для работы с ботом.\n\n"
                "Введите /help для получения списка доступных команд."
            )
            
    except Exception as e:
        logger.error(f"Ошибка в handle_text_message: {e}")

async def process_field_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка ввода поля шаблона"""
    try:
        user_id = update.effective_user.id
        state = user_states[user_id]
        template = state['template']
        fields = get_template_fields(template['id'])
        current_field_index = state['current_field']
        
        if current_field_index >= len(fields):
            return
        
        field = fields[current_field_index]
        user_input = update.message.text
        
        # Валидация ввода
        if field.get('required', True) and not user_input.strip():
            await update.message.reply_text(
                f"❌ Поле '{field['label']}' обязательно для заполнения. Попробуйте еще раз."
            )
            return
        
        # Сохранение значения поля
        state['fields'][field['name']] = user_input
        state['current_field'] += 1
        
        # Переход к следующему полю
        await ask_next_field_via_message(update, context)
        
    except Exception as e:
        logger.error(f"Ошибка в process_field_input: {e}")

async def ask_next_field_via_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Запрос следующего поля через новое сообщение"""
    try:
        user_id = update.effective_user.id
        if user_id not in user_states:
            return
        
        state = user_states[user_id]
        template = state['template']
        fields = get_template_fields(template['id'])
        current_field_index = state['current_field']
        
        if current_field_index >= len(fields):
            # Все поля заполнены, создаем пост
            await create_post_from_template(update, context)
            return
        
        field = fields[current_field_index]
        
        text = f"""
✅ Поле сохранено!

📝 **Создание поста: {template['name']}**

Шаг {current_field_index + 1} из {len(fields)}

**{field['label']}**
{field.get('description', '')}

{field.get('placeholder', 'Введите значение:')}
        """
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Отмена", callback_data="post_cancel")]
        ])
        
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в ask_next_field_via_message: {e}")

async def create_post_from_template(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Создание поста из заполненного шаблона"""
    try:
        user_id = update.effective_user.id
        if user_id not in user_states:
            return
        
        state = user_states[user_id]
        template = state['template']
        fields_data = state['fields']
        
        db = get_session()
        
        try:
            user_service = UserService(db)
            post_service = PostService(db)
            analytics_service = AnalyticsService(db)
            
            db_user = user_service.get_user_by_telegram_id(user_id)
            
            if not db_user:
                await update.message.reply_text("❌ Пользователь не найден.")
                return
            
            # Формирование контента поста из шаблона
            title = fields_data.get('title', 'Без названия')
            content = template['content_template'].format(**fields_data)
            
            # Создание поста
            post = post_service.create_post(
                title=title,
                content=content,
                author_id=db_user.id,
                template_type=template['id']
            )
            
            # Логирование активности
            analytics_service.log_user_activity(
                user_id=db_user.id,
                activity_type="post_create",
                activity_data={"post_id": post.id, "template": template['id']}
            )
            
            db.commit()
            
            # Очистка состояния
            del user_states[user_id]
            
            text = f"""
✅ **Пост успешно создан!**

📋 **Информация о посте:**
• Номер: #{post.post_number}
• Заголовок: {post.title}
• Шаблон: {template['name']}
• Статус: 🟡 Черновик

Пост создан как черновик. Вы можете опубликовать его позже.
            """
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🟢 Опубликовать", callback_data=f"post_publish_{post.post_number}"),
                    InlineKeyboardButton("✏️ Редактировать", callback_data=f"post_edit_{post.post_number}")
                ],
                [
                    InlineKeyboardButton("📝 Мои посты", callback_data="main_my_posts"),
                    InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
                ]
            ])
            
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в create_post_from_template: {e}")
        await update.message.reply_text("❌ Ошибка при создании поста.")

async def show_post_details(update: Update, context: ContextTypes.DEFAULT_TYPE, post_number: int) -> None:
    """Показ детальной информации о посте"""
    try:
        db = get_session()
        
        try:
            post_service = PostService(db)
            post = post_service.get_post_by_number(post_number)
            
            if not post:
                await update.callback_query.edit_message_text("❌ Пост не найден.")
                return
            
            status = "🟢 Опубликован" if post.is_published else "🟡 Черновик"
            author_name = post.author.first_name or post.author.username or "Аноним"
            
            text = f"""
📋 **Пост #{post.post_number}**

**{post.title}**

👤 Автор: {author_name}
📅 Создан: {post.created_at.strftime('%d.%m.%Y %H:%M')}
📊 Статус: {status}

**Содержание:**
{post.content}
            """
            
            keyboard_buttons = [
                [InlineKeyboardButton("🔙 Назад", callback_data="post_list_all")]
            ]
            
            # Добавляем кнопки действий для автора или админа
            user_service = UserService(db)
            db_user = user_service.get_user_by_telegram_id(update.effective_user.id)
            
            if db_user and (post.author_id == db_user.id or db_user.is_admin):
                keyboard_buttons.insert(0, [
                    InlineKeyboardButton("✏️ Редактировать", callback_data=f"post_edit_{post_number}"),
                    InlineKeyboardButton("🗑 Удалить", callback_data=f"post_delete_{post_number}")
                ])
                
                if not post.is_published:
                    keyboard_buttons.insert(1, [
                        InlineKeyboardButton("🟢 Опубликовать", callback_data=f"post_publish_{post_number}")
                    ])
            
            keyboard = InlineKeyboardMarkup(keyboard_buttons)
            
            await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в show_post_details: {e}")

async def toggle_post_publication(update: Update, context: ContextTypes.DEFAULT_TYPE, post_number: int) -> None:
    """Переключение статуса публикации поста"""
    try:
        db = get_session()
        
        try:
            user_service = UserService(db)
            post_service = PostService(db)
            analytics_service = AnalyticsService(db)
            
            db_user = user_service.get_user_by_telegram_id(update.effective_user.id)
            post = post_service.get_post_by_number(post_number)
            
            if not post or not db_user:
                await update.callback_query.edit_message_text("❌ Пост или пользователь не найден.")
                return
            
            # Проверка прав доступа
            if post.author_id != db_user.id and not db_user.is_admin:
                await update.callback_query.answer("❌ Недостаточно прав", show_alert=True)
                return
            
            # Переключение статуса
            success = post_service.toggle_post_publication(post_number)
            
            if success:
                # Логирование активности
                action = "publish" if not post.is_published else "unpublish"
                analytics_service.log_user_activity(
                    user_id=db_user.id,
                    activity_type=f"post_{action}",
                    activity_data={"post_id": post.id}
                )
                
                db.commit()
                
                status_text = "опубликован" if not post.is_published else "снят с публикации"
                await update.callback_query.answer(f"✅ Пост {status_text}", show_alert=True)
                
                # Обновление сообщения
                await show_post_details(update, context, post_number)
            else:
                await update.callback_query.answer("❌ Ошибка при изменении статуса", show_alert=True)
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в toggle_post_publication: {e}")
