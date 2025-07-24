"""
Шаблоны для создания постов
"""

from typing import List, Dict, Any, Optional

def get_post_templates() -> List[Dict[str, Any]]:
    """Получение списка доступных шаблонов постов"""
    templates = [
        {
            'id': 'news',
            'name': 'Новость',
            'description': 'Шаблон для новостных сообщений',
            'icon': '📰',
            'content_template': """📰 **{title}**

📅 **Дата:** {date}
📍 **Место:** {location}

📋 **Краткое описание:**
{summary}

📝 **Подробности:**
{content}

🔗 **Источник:** {source}

#новости #{category}"""
        },
        {
            'id': 'article',
            'name': 'Статья',
            'description': 'Шаблон для развернутых статей и аналитических материалов',
            'icon': '📝',
            'content_template': """📝 **{title}**

👤 **Автор:** {author}
📅 **Дата публикации:** {date}
⏱ **Время чтения:** {reading_time}

📋 **Аннотация:**
{abstract}

📖 **Содержание:**

{intro}

**Основная часть:**
{main_content}

**Заключение:**
{conclusion}

🏷 **Теги:** #{tag1} #{tag2} #{tag3}

📚 **Источники:**
{sources}"""
        },
        {
            'id': 'announcement',
            'name': 'Объявление',
            'description': 'Шаблон для важных объявлений и уведомлений',
            'icon': '📢',
            'content_template': """📢 **ОБЪЯВЛЕНИЕ**

🎯 **{title}**

⚠️ **Важность:** {priority}
📅 **Дата:** {date}
⏰ **Время:** {time}

📋 **Детали:**
{details}

👥 **Для кого:** {target_audience}

📍 **Место:** {location}

📞 **Контакты для связи:**
{contacts}

⚡ **Срочность:** {urgency}

#объявление #{category}"""
        },
        {
            'id': 'review',
            'name': 'Обзор',
            'description': 'Шаблон для обзоров товаров, услуг, мероприятий',
            'icon': '⭐',
            'content_template': """⭐ **ОБЗОР: {title}**

📊 **Общая оценка:** {rating}/10

📋 **Краткая характеристика:**
{description}

✅ **Плюсы:**
{pros}

❌ **Минусы:**
{cons}

💰 **Цена/Стоимость:** {price}

🎯 **Кому подойдет:** {target_audience}

📝 **Детальное мнение:**
{detailed_review}

🏆 **Итоговая рекомендация:**
{recommendation}

#обзор #{category} #рейтинг"""
        },
        {
            'id': 'tutorial',
            'name': 'Руководство',
            'description': 'Шаблон для обучающих материалов и инструкций',
            'icon': '📚',
            'content_template': """📚 **РУКОВОДСТВО: {title}**

🎯 **Цель:** {objective}
⏱ **Время выполнения:** {duration}
📊 **Уровень сложности:** {difficulty}

🛠 **Что понадобится:**
{requirements}

📋 **Пошаговая инструкция:**

**Шаг 1:** {step1}

**Шаг 2:** {step2}

**Шаг 3:** {step3}

**Шаг 4:** {step4}

💡 **Полезные советы:**
{tips}

⚠️ **Важные моменты:**
{warnings}

🏁 **Результат:**
{result}

#руководство #{category} #обучение"""
        },
        {
            'id': 'event',
            'name': 'Мероприятие',
            'description': 'Шаблон для анонсов и отчетов о мероприятиях',
            'icon': '🎉',
            'content_template': """🎉 **МЕРОПРИЯТИЕ: {title}**

📅 **Дата:** {date}
⏰ **Время:** {start_time} - {end_time}
📍 **Место:** {venue}

📋 **Описание:**
{description}

👥 **Целевая аудитория:** {target_audience}

🎫 **Участие:**
{participation_info}

💰 **Стоимость:** {cost}

📝 **Программа:**
{program}

📞 **Контакты для записи:**
{contacts}

🔗 **Дополнительная информация:**
{additional_info}

#мероприятие #{category} #событие"""
        }
    ]
    
    return templates

def get_template_fields(template_id: str) -> List[Dict[str, Any]]:
    """Получение полей конкретного шаблона"""
    
    fields_map = {
        'news': [
            {
                'name': 'title',
                'label': '📰 Заголовок новости',
                'description': 'Краткий и информативный заголовок',
                'placeholder': 'Введите заголовок новости...',
                'required': True,
                'type': 'text'
            },
            {
                'name': 'date',
                'label': '📅 Дата события',
                'description': 'Когда произошло событие',
                'placeholder': 'Например: 15 декабря 2024',
                'required': True,
                'type': 'text'
            },
            {
                'name': 'location',
                'label': '📍 Место события',
                'description': 'Где произошло событие',
                'placeholder': 'Город, адрес или регион',
                'required': False,
                'type': 'text'
            },
            {
                'name': 'summary',
                'label': '📋 Краткое описание',
                'description': 'Суть новости в 2-3 предложениях',
                'placeholder': 'Опишите суть события кратко...',
                'required': True,
                'type': 'textarea'
            },
            {
                'name': 'content',
                'label': '📝 Подробности',
                'description': 'Детальное описание события',
                'placeholder': 'Расскажите подробно о событии...',
                'required': True,
                'type': 'textarea'
            },
            {
                'name': 'source',
                'label': '🔗 Источник',
                'description': 'Источник информации',
                'placeholder': 'Ссылка или название источника',
                'required': False,
                'type': 'text'
            },
            {
                'name': 'category',
                'label': '🏷 Категория',
                'description': 'Тематическая категория новости',
                'placeholder': 'политика, спорт, технологии...',
                'required': False,
                'type': 'text'
            }
        ],
        
        'article': [
            {
                'name': 'title',
                'label': '📝 Название статьи',
                'description': 'Заголовок вашей статьи',
                'placeholder': 'Введите название статьи...',
                'required': True,
                'type': 'text'
            },
            {
                'name': 'author',
                'label': '👤 Автор',
                'description': 'Имя автора статьи',
                'placeholder': 'Ваше имя или псевдоним',
                'required': True,
                'type': 'text'
            },
            {
                'name': 'date',
                'label': '📅 Дата публикации',
                'description': 'Дата написания статьи',
                'placeholder': 'Например: 15 декабря 2024',
                'required': True,
                'type': 'text'
            },
            {
                'name': 'reading_time',
                'label': '⏱ Время чтения',
                'description': 'Примерное время чтения',
                'placeholder': '5-10 минут',
                'required': False,
                'type': 'text'
            },
            {
                'name': 'abstract',
                'label': '📋 Аннотация',
                'description': 'Краткое описание содержания статьи',
                'placeholder': 'О чем эта статья...',
                'required': True,
                'type': 'textarea'
            },
            {
                'name': 'intro',
                'label': '🚀 Введение',
                'description': 'Вводная часть статьи',
                'placeholder': 'Введение к теме...',
                'required': True,
                'type': 'textarea'
            },
            {
                'name': 'main_content',
                'label': '📖 Основная часть',
                'description': 'Основное содержание статьи',
                'placeholder': 'Основной текст статьи...',
                'required': True,
                'type': 'textarea'
            },
            {
                'name': 'conclusion',
                'label': '🏁 Заключение',
                'description': 'Выводы и заключительные мысли',
                'placeholder': 'Подведите итоги...',
                'required': True,
                'type': 'textarea'
            },
            {
                'name': 'tag1',
                'label': '🏷 Тег 1',
                'description': 'Первый тематический тег',
                'placeholder': 'технологии',
                'required': False,
                'type': 'text'
            },
            {
                'name': 'tag2',
                'label': '🏷 Тег 2',
                'description': 'Второй тематический тег',
                'placeholder': 'аналитика',
                'required': False,
                'type': 'text'
            },
            {
                'name': 'tag3',
                'label': '🏷 Тег 3',
                'description': 'Третий тематический тег',
                'placeholder': 'исследование',
                'required': False,
                'type': 'text'
            },
            {
                'name': 'sources',
                'label': '📚 Источники',
                'description': 'Список использованных источников',
                'placeholder': 'Ссылки на источники...',
                'required': False,
                'type': 'textarea'
            }
        ],
        
        'announcement': [
            {
                'name': 'title',
                'label': '📢 Заголовок объявления',
                'description': 'Краткий и ясный заголовок',
                'placeholder': 'О чем объявление...',
                'required': True,
                'type': 'text'
            },
            {
                'name': 'priority',
                'label': '⚠️ Уровень важности',
                'description': 'Насколько важно это объявление',
                'placeholder': 'Высокая / Средняя / Низкая',
                'required': True,
                'type': 'text'
            },
            {
                'name': 'date',
                'label': '📅 Дата',
                'description': 'Дата события или объявления',
                'placeholder': '15 декабря 2024',
                'required': True,
                'type': 'text'
            },
            {
                'name': 'time',
                'label': '⏰ Время',
                'description': 'Время события (если применимо)',
                'placeholder': '14:00',
                'required': False,
                'type': 'text'
            },
            {
                'name': 'details',
                'label': '📋 Детали',
                'description': 'Подробная информация',
                'placeholder': 'Подробно опишите объявление...',
                'required': True,
                'type': 'textarea'
            },
            {
                'name': 'target_audience',
                'label': '👥 Целевая аудитория',
                'description': 'Для кого это объявление',
                'placeholder': 'Для всех сотрудников / Для студентов...',
                'required': True,
                'type': 'text'
            },
            {
                'name': 'location',
                'label': '📍 Место',
                'description': 'Где происходит событие',
                'placeholder': 'Адрес или место проведения',
                'required': False,
                'type': 'text'
            },
            {
                'name': 'contacts',
                'label': '📞 Контакты',
                'description': 'Контактная информация',
                'placeholder': 'Телефон, email, имя ответственного...',
                'required': False,
                'type': 'textarea'
            },
            {
                'name': 'urgency',
                'label': '⚡ Срочность',
                'description': 'Насколько срочно',
                'placeholder': 'До конца дня / В течение недели...',
                'required': False,
                'type': 'text'
            },
            {
                'name': 'category',
                'label': '🏷 Категория',
                'description': 'Тип объявления',
                'placeholder': 'работа, учеба, мероприятие...',
                'required': False,
                'type': 'text'
            }
        ],
        
        'review': [
            {
                'name': 'title',
                'label': '⭐ Название обзора',
                'description': 'Что вы обозреваете',
                'placeholder': 'Название товара/услуги/события...',
                'required': True,
                'type': 'text'
            },
            {
                'name': 'rating',
                'label': '📊 Оценка (1-10)',
                'description': 'Ваша общая оценка по 10-балльной шкале',
                'placeholder': '8',
                'required': True,
                'type': 'text'
            },
            {
                'name': 'description',
                'label': '📋 Краткая характеристика',
                'description': 'Что это такое в нескольких словах',
                'placeholder': 'Краткое описание...',
                'required': True,
                'type': 'textarea'
            },
            {
                'name': 'pros',
                'label': '✅ Плюсы',
                'description': 'Что вам понравилось',
                'placeholder': '• Первый плюс\n• Второй плюс...',
                'required': True,
                'type': 'textarea'
            },
            {
                'name': 'cons',
                'label': '❌ Минусы',
                'description': 'Что не понравилось',
                'placeholder': '• Первый минус\n• Второй минус...',
                'required': True,
                'type': 'textarea'
            },
            {
                'name': 'price',
                'label': '💰 Цена/Стоимость',
                'description': 'Сколько это стоит',
                'placeholder': '1000 рублей / Бесплатно...',
                'required': False,
                'type': 'text'
            },
            {
                'name': 'target_audience',
                'label': '🎯 Кому подойдет',
                'description': 'Для какой аудитории это подходит',
                'placeholder': 'Начинающим / Профессионалам...',
                'required': False,
                'type': 'text'
            },
            {
                'name': 'detailed_review',
                'label': '📝 Детальное мнение',
                'description': 'Развернутый отзыв',
                'placeholder': 'Подробно расскажите о своем опыте...',
                'required': True,
                'type': 'textarea'
            },
            {
                'name': 'recommendation',
                'label': '🏆 Рекомендация',
                'description': 'Ваша итоговая рекомендация',
                'placeholder': 'Рекомендую / Не рекомендую потому что...',
                'required': True,
                'type': 'textarea'
            },
            {
                'name': 'category',
                'label': '🏷 Категория',
                'description': 'К какой категории относится',
                'placeholder': 'технологии, еда, развлечения...',
                'required': False,
                'type': 'text'
            }
        ],
        
        'tutorial': [
            {
                'name': 'title',
                'label': '📚 Название руководства',
                'description': 'Что вы будете объяснять',
                'placeholder': 'Как сделать...',
                'required': True,
                'type': 'text'
            },
            {
                'name': 'objective',
                'label': '🎯 Цель',
                'description': 'Чего достигнет читатель',
                'placeholder': 'После прочтения вы сможете...',
                'required': True,
                'type': 'text'
            },
            {
                'name': 'duration',
                'label': '⏱ Время выполнения',
                'description': 'Сколько времени потребуется',
                'placeholder': '30 минут',
                'required': False,
                'type': 'text'
            },
            {
                'name': 'difficulty',
                'label': '📊 Уровень сложности',
                'description': 'Насколько сложно это выполнить',
                'placeholder': 'Легко / Средне / Сложно',
                'required': True,
                'type': 'text'
            },
            {
                'name': 'requirements',
                'label': '🛠 Что понадобится',
                'description': 'Необходимые инструменты, знания, материалы',
                'placeholder': '• Компьютер\n• Программа X\n• Базовые знания...',
                'required': True,
                'type': 'textarea'
            },
            {
                'name': 'step1',
                'label': '1️⃣ Шаг 1',
                'description': 'Первый шаг инструкции',
                'placeholder': 'Опишите первое действие...',
                'required': True,
                'type': 'textarea'
            },
            {
                'name': 'step2',
                'label': '2️⃣ Шаг 2',
                'description': 'Второй шаг инструкции',
                'placeholder': 'Опишите второе действие...',
                'required': True,
                'type': 'textarea'
            },
            {
                'name': 'step3',
                'label': '3️⃣ Шаг 3',
                'description': 'Третий шаг инструкции',
                'placeholder': 'Опишите третье действие...',
                'required': True,
                'type': 'textarea'
            },
            {
                'name': 'step4',
                'label': '4️⃣ Шаг 4',
                'description': 'Четвертый шаг (если нужен)',
                'placeholder': 'Опишите четвертое действие или оставьте пустым...',
                'required': False,
                'type': 'textarea'
            },
            {
                'name': 'tips',
                'label': '💡 Полезные советы',
                'description': 'Дополнительные рекомендации',
                'placeholder': 'Советы для лучшего результата...',
                'required': False,
                'type': 'textarea'
            },
            {
                'name': 'warnings',
                'label': '⚠️ Важные моменты',
                'description': 'На что обратить особое внимание',
                'placeholder': 'Чего следует избегать...',
                'required': False,
                'type': 'textarea'
            },
            {
                'name': 'result',
                'label': '🏁 Ожидаемый результат',
                'description': 'Что получится в итоге',
                'placeholder': 'В результате у вас будет...',
                'required': True,
                'type': 'textarea'
            },
            {
                'name': 'category',
                'label': '🏷 Категория',
                'description': 'Тематическая категория',
                'placeholder': 'программирование, дизайн, готовка...',
                'required': False,
                'type': 'text'
            }
        ],
        
        'event': [
            {
                'name': 'title',
                'label': '🎉 Название мероприятия',
                'description': 'Как называется ваше мероприятие',
                'placeholder': 'Название события...',
                'required': True,
                'type': 'text'
            },
            {
                'name': 'date',
                'label': '📅 Дата проведения',
                'description': 'Когда состоится мероприятие',
                'placeholder': '15 декабря 2024',
                'required': True,
                'type': 'text'
            },
            {
                'name': 'start_time',
                'label': '⏰ Время начала',
                'description': 'Во сколько начинается',
                'placeholder': '18:00',
                'required': True,
                'type': 'text'
            },
            {
                'name': 'end_time',
                'label': '🏁 Время окончания',
                'description': 'Во сколько заканчивается',
                'placeholder': '21:00',
                'required': False,
                'type': 'text'
            },
            {
                'name': 'venue',
                'label': '📍 Место проведения',
                'description': 'Где состоится мероприятие',
                'placeholder': 'Адрес или название места...',
                'required': True,
                'type': 'text'
            },
            {
                'name': 'description',
                'label': '📋 Описание',
                'description': 'Что это за мероприятие',
                'placeholder': 'Опишите суть мероприятия...',
                'required': True,
                'type': 'textarea'
            },
            {
                'name': 'target_audience',
                'label': '👥 Целевая аудитория',
                'description': 'Для кого предназначено',
                'placeholder': 'Для студентов, специалистов...',
                'required': False,
                'type': 'text'
            },
            {
                'name': 'participation_info',
                'label': '🎫 Условия участия',
                'description': 'Как принять участие',
                'placeholder': 'Регистрация обязательна / Свободный вход...',
                'required': True,
                'type': 'textarea'
            },
            {
                'name': 'cost',
                'label': '💰 Стоимость',
                'description': 'Сколько стоит участие',
                'placeholder': 'Бесплатно / 500 рублей...',
                'required': False,
                'type': 'text'
            },
            {
                'name': 'program',
                'label': '📝 Программа',
                'description': 'План мероприятия',
                'placeholder': 'Расписание и программа...',
                'required': False,
                'type': 'textarea'
            },
            {
                'name': 'contacts',
                'label': '📞 Контакты',
                'description': 'Как связаться для записи',
                'placeholder': 'Телефон, email...',
                'required': False,
                'type': 'textarea'
            },
            {
                'name': 'additional_info',
                'label': '🔗 Дополнительно',
                'description': 'Дополнительная информация',
                'placeholder': 'Ссылки, особые условия...',
                'required': False,
                'type': 'textarea'
            },
            {
                'name': 'category',
                'label': '🏷 Категория',
                'description': 'Тип мероприятия',
                'placeholder': 'конференция, семинар, концерт...',
                'required': False,
                'type': 'text'
            }
        ]
    }
    
    return fields_map.get(template_id, [])

def get_template_by_id(template_id: str) -> Optional[Dict[str, Any]]:
    """Получение шаблона по ID"""
    templates = get_post_templates()
    return next((t for t in templates if t['id'] == template_id), None)

def validate_template_data(template_id: str, data: Dict[str, str]) -> Dict[str, Any]:
    """Валидация данных шаблона"""
    fields = get_template_fields(template_id)
    errors = []
    warnings = []
    
    # Проверка обязательных полей
    for field in fields:
        field_name = field['name']
        if field.get('required', False):
            if not data.get(field_name) or not data[field_name].strip():
                errors.append(f"Поле '{field['label']}' обязательно для заполнения")
    
    # Проверка длины полей
    for field_name, value in data.items():
        if value and len(value) > 2000:  # Ограничение на длину
            warnings.append(f"Поле '{field_name}' очень длинное ({len(value)} символов)")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

def get_template_preview(template_id: str, data: Dict[str, str]) -> str:
    """Получение превью поста по шаблону"""
    template = get_template_by_id(template_id)
    if not template:
        return "Шаблон не найден"
    
    try:
        # Заполнение пустых значений
        filled_data = {}
        for key, value in data.items():
            filled_data[key] = value if value else f"[{key}]"
        
        # Форматирование шаблона
        preview = template['content_template'].format(**filled_data)
        return preview
    except KeyError as e:
        return f"Ошибка в шаблоне: отсутствует поле {e}"
    except Exception as e:
        return f"Ошибка при генерации превью: {e}"

def get_template_statistics() -> List[Dict[str, Any]]:
    """Получение статистики использования шаблонов"""
    # Эта функция должна быть интегрирована с базой данных
    # Здесь возвращаем базовую структуру
    templates = get_post_templates()
    
    return [
        {
            'id': template['id'],
            'name': template['name'],
            'usage_count': 0,  # Будет заполнено из БД
            'last_used': None,  # Будет заполнено из БД
            'avg_completion_rate': 0  # Процент заполнения полей
        }
        for template in templates
    ]

def search_templates(query: str) -> List[Dict[str, Any]]:
    """Поиск шаблонов по названию или описанию"""
    templates = get_post_templates()
    query_lower = query.lower()
    
    matching_templates = []
    for template in templates:
        if (query_lower in template['name'].lower() or 
            query_lower in template['description'].lower()):
            matching_templates.append(template)
    
    return matching_templates

def get_recommended_templates(user_history: List[str] = None) -> List[Dict[str, Any]]:
    """Получение рекомендованных шаблонов на основе истории пользователя"""
    templates = get_post_templates()
    
    if not user_history:
        # Возвращаем самые популярные шаблоны по умолчанию
        return templates[:3]
    
    # Простая логика рекомендаций - исключаем недавно использованные
    unused_templates = [t for t in templates if t['id'] not in user_history[-3:]]
    
    return unused_templates[:3] if unused_templates else templates[:3]
