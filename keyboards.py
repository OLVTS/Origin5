"""
Клавиатуры для Telegram бота
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Optional

def get_main_menu_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    """Получение основной клавиатуры меню"""
    keyboard = [
        [
            InlineKeyboardButton("📝 Добавить объект", callback_data="post_create"),
            InlineKeyboardButton("📋 Мои объекты", callback_data="main_my_posts")
        ],
        [
            InlineKeyboardButton("📰 Все посты", callback_data="post_list_all"),
            InlineKeyboardButton("📊 Аналитика", callback_data="analytics_general")
        ],
        [
            InlineKeyboardButton("👤 Профиль", callback_data="main_profile"),
            InlineKeyboardButton("❓ Помощь", callback_data="main_help")
        ]
    ]
    
    # Добавление админских кнопок
    if is_admin:
        admin_row = [
            InlineKeyboardButton("👑 Админ-панель", callback_data="admin_panel"),
            InlineKeyboardButton("📈 Расширенная аналитика", callback_data="analytics_advanced")
        ]
        keyboard.insert(-1, admin_row)  # Вставляем перед последней строкой
    
    return InlineKeyboardMarkup(keyboard)

def get_posts_keyboard(show_admin_actions: bool = False) -> InlineKeyboardMarkup:
    """Получение клавиатуры для работы с постами"""
    keyboard = [
        [
            InlineKeyboardButton("➕ Добавить объект", callback_data="post_create"),
            InlineKeyboardButton("📋 Мои объекты", callback_data="post_list_my")
        ],
        [
            InlineKeyboardButton("📰 Все посты", callback_data="post_list_all"),
            InlineKeyboardButton("🔍 Поиск", callback_data="post_search")
        ]
    ]
    
    if show_admin_actions:
        admin_row = [
            InlineKeyboardButton("⏳ На модерации", callback_data="post_list_pending"),
            InlineKeyboardButton("🗑 Удаленные", callback_data="post_list_deleted")
        ]
        keyboard.append(admin_row)
    
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)

def get_post_actions_keyboard(post, is_admin: bool = False) -> InlineKeyboardMarkup:
    """Получение клавиатуры действий для конкретного поста"""
    keyboard = []
    
    # Основные действия
    action_row = [
        InlineKeyboardButton("✏️ Редактировать", callback_data=f"post_edit_{post.post_number}"),
        InlineKeyboardButton("👁 Просмотр", callback_data=f"post_view_{post.post_number}")
    ]
    keyboard.append(action_row)
    
    # Публикация/снятие с публикации
    if post.is_published:
        keyboard.append([
            InlineKeyboardButton("🟡 Снять с публикации", callback_data=f"post_unpublish_{post.post_number}")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton("🟢 Опубликовать", callback_data=f"post_publish_{post.post_number}")
        ])
    
    # Удаление
    delete_row = [InlineKeyboardButton("🗑 Удалить", callback_data=f"post_delete_{post.post_number}")]
    
    # Админские действия
    if is_admin:
        delete_row.append(
            InlineKeyboardButton("💀 Удалить навсегда", callback_data=f"post_hard_delete_{post.post_number}")
        )
    
    keyboard.append(delete_row)
    
    # Навигация
    keyboard.append([
        InlineKeyboardButton("🔙 Назад", callback_data="main_my_objects"),
        InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
    ])
    
    return InlineKeyboardMarkup(keyboard)

def get_post_list_keyboard(posts: List, page: int = 0, posts_per_page: int = 5, 
                          callback_prefix: str = "post_view") -> InlineKeyboardMarkup:
    """Получение клавиатуры для списка постов с пагинацией"""
    keyboard = []
    
    # Посты на текущей странице
    start_idx = page * posts_per_page
    end_idx = start_idx + posts_per_page
    page_posts = posts[start_idx:end_idx]
    
    for post in page_posts:
        status_emoji = "🟢" if post.is_published else "🟡"
        button_text = f"{status_emoji} #{post.post_number} - {post.title[:25]}..."
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"{callback_prefix}_{post.post_number}")
        ])
    
    # Навигация по страницам
    if len(posts) > posts_per_page:
        nav_buttons = []
        
        if page > 0:
            nav_buttons.append(
                InlineKeyboardButton("⬅️ Назад", callback_data=f"post_page_{page-1}")
            )
        
        # Информация о странице
        total_pages = (len(posts) - 1) // posts_per_page + 1
        nav_buttons.append(
            InlineKeyboardButton(f"📄 {page + 1}/{total_pages}", callback_data="post_page_info")
        )
        
        if end_idx < len(posts):
            nav_buttons.append(
                InlineKeyboardButton("➡️ Вперед", callback_data=f"post_page_{page+1}")
            )
        
        keyboard.append(nav_buttons)
    
    # Основные действия
    keyboard.append([
        InlineKeyboardButton("➕ Добавить объект", callback_data="post_create"),
        InlineKeyboardButton("🔄 Обновить", callback_data="post_list_refresh")
    ])
    
    # Возврат в главное меню
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Получение административной клавиатуры"""
    keyboard = [
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
            InlineKeyboardButton("🔧 Шаблоны", callback_data="admin_templates")
        ],
        [
            InlineKeyboardButton("📈 Метрики", callback_data="admin_metrics"),
            InlineKeyboardButton("🗄 База данных", callback_data="admin_database")
        ],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def get_user_management_keyboard() -> InlineKeyboardMarkup:
    """Получение клавиатуры управления пользователями"""
    keyboard = [
        [
            InlineKeyboardButton("👑 Назначить админа", callback_data="admin_user_promote"),
            InlineKeyboardButton("👤 Снять права", callback_data="admin_user_demote")
        ],
        [
            InlineKeyboardButton("🔒 Заблокировать", callback_data="admin_user_block"),
            InlineKeyboardButton("🔓 Разблокировать", callback_data="admin_user_unblock")
        ],
        [
            InlineKeyboardButton("📊 Статистика", callback_data="admin_user_stats"),
            InlineKeyboardButton("🔍 Поиск", callback_data="admin_user_search")
        ],
        [
            InlineKeyboardButton("📤 Экспорт", callback_data="admin_export_users"),
            InlineKeyboardButton("🔄 Обновить", callback_data="admin_users")
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def get_post_management_keyboard() -> InlineKeyboardMarkup:
    """Получение клавиатуры управления постами"""
    keyboard = [
        [
            InlineKeyboardButton("📋 Все посты", callback_data="admin_posts_all"),
            InlineKeyboardButton("⏳ На модерации", callback_data="admin_posts_pending")
        ],
        [
            InlineKeyboardButton("🟢 Опубликованные", callback_data="admin_posts_published"),
            InlineKeyboardButton("🟡 Черновики", callback_data="admin_posts_drafts")
        ],
        [
            InlineKeyboardButton("🗑 Удаленные", callback_data="admin_posts_deleted"),
            InlineKeyboardButton("📊 Статистика", callback_data="admin_posts_stats")
        ],
        [
            InlineKeyboardButton("📤 Экспорт", callback_data="admin_export_posts"),
            InlineKeyboardButton("🔄 Обновить", callback_data="admin_posts")
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def get_analytics_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    """Получение клавиатуры аналитики"""
    keyboard = [
        [
            InlineKeyboardButton("👤 Моя статистика", callback_data="analytics_personal"),
            InlineKeyboardButton("📈 Графики", callback_data="analytics_charts")
        ]
    ]
    
    if is_admin:
        keyboard.extend([
            [
                InlineKeyboardButton("👥 Пользователи", callback_data="analytics_users"),
                InlineKeyboardButton("📝 Посты", callback_data="analytics_posts")
            ],
            [
                InlineKeyboardButton("🔥 Тренды", callback_data="analytics_trends"),
                InlineKeyboardButton("📊 Детальная", callback_data="analytics_detailed")
            ],
            [
                InlineKeyboardButton("📤 Экспорт", callback_data="analytics_export"),
                InlineKeyboardButton("📋 Отчеты", callback_data="analytics_reports")
            ]
        ])
    
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)

def get_template_selection_keyboard(templates: List[dict]) -> InlineKeyboardMarkup:
    """Получение клавиатуры выбора шаблона"""
    keyboard = []
    
    for template in templates:
        keyboard.append([
            InlineKeyboardButton(
                f"📋 {template['name']}", 
                callback_data=f"post_template_{template['id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="post_cancel")])
    
    return InlineKeyboardMarkup(keyboard)

def get_confirmation_keyboard(action: str, item_id: str) -> InlineKeyboardMarkup:
    """Получение клавиатуры подтверждения действия"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Да", callback_data=f"{action}_confirm_{item_id}"),
            InlineKeyboardButton("❌ Нет", callback_data=f"{action}_cancel_{item_id}")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def get_export_keyboard() -> InlineKeyboardMarkup:
    """Получение клавиатуры экспорта данных"""
    keyboard = [
        [
            InlineKeyboardButton("👥 Пользователи (CSV)", callback_data="analytics_export_users_csv"),
            InlineKeyboardButton("📝 Посты (CSV)", callback_data="analytics_export_posts_csv")
        ],
        [
            InlineKeyboardButton("📊 Аналитика (JSON)", callback_data="analytics_export_analytics_json"),
            InlineKeyboardButton("📈 Графики (PNG)", callback_data="analytics_export_charts_png")
        ],
        [
            InlineKeyboardButton("📋 Полный отчет (PDF)", callback_data="analytics_export_full_pdf"),
            InlineKeyboardButton("💾 Полный дамп", callback_data="analytics_export_full_dump")
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data="analytics_general")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Получение клавиатуры настроек"""
    keyboard = [
        [
            InlineKeyboardButton("📋 Шаблоны постов", callback_data="admin_templates"),
            InlineKeyboardButton("🔔 Уведомления", callback_data="admin_notifications")
        ],
        [
            InlineKeyboardButton("⏰ Автоматизация", callback_data="admin_automation"),
            InlineKeyboardButton("💾 Резервные копии", callback_data="admin_backups")
        ],
        [
            InlineKeyboardButton("🔧 Конфигурация", callback_data="admin_config"),
            InlineKeyboardButton("🗄 База данных", callback_data="admin_database")
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def get_pagination_keyboard(current_page: int, total_pages: int, 
                           callback_prefix: str) -> InlineKeyboardMarkup:
    """Получение клавиатуры пагинации"""
    keyboard = []
    
    nav_buttons = []
    
    # Кнопка "Назад"
    if current_page > 0:
        nav_buttons.append(
            InlineKeyboardButton("⬅️", callback_data=f"{callback_prefix}_page_{current_page - 1}")
        )
    
    # Информация о странице
    nav_buttons.append(
        InlineKeyboardButton(f"{current_page + 1}/{total_pages}", callback_data="page_info")
    )
    
    # Кнопка "Вперед"
    if current_page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton("➡️", callback_data=f"{callback_prefix}_page_{current_page + 1}")
        )
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard(callback_data: str = "main_menu") -> InlineKeyboardMarkup:
    """Получение простой клавиатуры с кнопкой назад"""
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data=callback_data)]]
    return InlineKeyboardMarkup(keyboard)

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Получение клавиатуры с кнопкой отмены"""
    keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)
