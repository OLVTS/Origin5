"""
Декораторы для проверки прав доступа
"""

from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from database import get_session
from services.user_service import UserService
import logging

logger = logging.getLogger(__name__)

def admin_required(func):
    """Декоратор для проверки прав администратора"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            user_id = update.effective_user.id
            db = get_session()
            
            try:
                user_service = UserService(db)
                db_user = user_service.get_user_by_telegram_id(user_id)
                
                if not db_user:
                    # Пользователь не найден в базе данных
                    if update.message:
                        await update.message.reply_text(
                            "❌ Пользователь не найден в системе. Используйте /start для регистрации."
                        )
                    elif update.callback_query:
                        await update.callback_query.answer(
                            "❌ Пользователь не найден в системе.", 
                            show_alert=True
                        )
                    return
                
                if not db_user.is_admin:
                    # Пользователь не является администратором
                    error_message = "❌ Недостаточно прав. Эта команда доступна только администраторам."
                    
                    if update.message:
                        await update.message.reply_text(error_message)
                    elif update.callback_query:
                        await update.callback_query.answer(error_message, show_alert=True)
                    return
                
                if not db_user.is_active:
                    # Пользователь заблокирован
                    error_message = "❌ Ваш аккаунт заблокирован. Обратитесь к администратору."
                    
                    if update.message:
                        await update.message.reply_text(error_message)
                    elif update.callback_query:
                        await update.callback_query.answer(error_message, show_alert=True)
                    return
                
                # Обновление времени последней активности
                user_service.update_last_activity(user_id)
                db.commit()
                
                # Вызов оригинальной функции
                return await func(update, context, *args, **kwargs)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Ошибка в декораторе admin_required: {e}")
            
            error_message = "❌ Произошла ошибка при проверке прав доступа."
            
            if update.message:
                await update.message.reply_text(error_message)
            elif update.callback_query:
                await update.callback_query.answer(error_message, show_alert=True)
    
    return wrapper

def active_user_required(func):
    """Декоратор для проверки активности пользователя"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            user_id = update.effective_user.id
            db = get_session()
            
            try:
                user_service = UserService(db)
                db_user = user_service.get_user_by_telegram_id(user_id)
                
                if not db_user:
                    # Пользователь не найден в базе данных
                    if update.message:
                        await update.message.reply_text(
                            "❌ Пользователь не найден в системе. Используйте /start для регистрации."
                        )
                    elif update.callback_query:
                        await update.callback_query.answer(
                            "❌ Пользователь не найден в системе.", 
                            show_alert=True
                        )
                    return
                
                if not db_user.is_active:
                    # Пользователь заблокирован
                    error_message = "❌ Ваш аккаунт заблокирован. Обратитесь к администратору."
                    
                    if update.message:
                        await update.message.reply_text(error_message)
                    elif update.callback_query:
                        await update.callback_query.answer(error_message, show_alert=True)
                    return
                
                # Обновление времени последней активности
                user_service.update_last_activity(user_id)
                db.commit()
                
                # Вызов оригинальной функции
                return await func(update, context, *args, **kwargs)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Ошибка в декораторе active_user_required: {e}")
            
            error_message = "❌ Произошла ошибка при проверке статуса пользователя."
            
            if update.message:
                await update.message.reply_text(error_message)
            elif update.callback_query:
                await update.callback_query.answer(error_message, show_alert=True)
    
    return wrapper

def rate_limit(max_calls: int = 10, time_window: int = 60):
    """
    Декоратор для ограничения частоты вызовов
    
    Args:
        max_calls: Максимальное количество вызовов
        time_window: Временное окно в секундах
    """
    from collections import defaultdict
    from time import time
    
    call_history = defaultdict(list)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id
            current_time = time()
            
            # Очистка старых записей
            call_history[user_id] = [
                call_time for call_time in call_history[user_id]
                if current_time - call_time < time_window
            ]
            
            # Проверка лимита
            if len(call_history[user_id]) >= max_calls:
                error_message = f"❌ Слишком много запросов. Попробуйте через {time_window} секунд."
                
                if update.message:
                    await update.message.reply_text(error_message)
                elif update.callback_query:
                    await update.callback_query.answer(error_message, show_alert=True)
                return
            
            # Добавление текущего вызова
            call_history[user_id].append(current_time)
            
            # Вызов оригинальной функции
            return await func(update, context, *args, **kwargs)
        
        return wrapper
    return decorator

def log_user_action(action_type: str):
    """
    Декоратор для логирования действий пользователя
    
    Args:
        action_type: Тип действия для логирования
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            try:
                user_id = update.effective_user.id
                
                # Вызов оригинальной функции
                result = await func(update, context, *args, **kwargs)
                
                # Логирование действия после успешного выполнения
                db = get_session()
                try:
                    from services.analytics_service import AnalyticsService
                    from services.user_service import UserService
                    
                    user_service = UserService(db)
                    analytics_service = AnalyticsService(db)
                    
                    db_user = user_service.get_user_by_telegram_id(user_id)
                    if db_user:
                        # Подготовка дополнительных данных
                        activity_data = {
                            'function_name': func.__name__,
                            'timestamp': str(current_time()),
                            'args_count': len(args),
                            'kwargs_keys': list(kwargs.keys()) if kwargs else []
                        }
                        
                        # Добавление данных из контекста, если есть
                        if hasattr(context, 'args') and context.args:
                            activity_data['command_args'] = context.args
                        
                        analytics_service.log_user_activity(
                            user_id=db_user.id,
                            activity_type=action_type,
                            activity_data=activity_data
                        )
                        
                        db.commit()
                
                except Exception as log_error:
                    logger.error(f"Ошибка при логировании действия {action_type}: {log_error}")
                    db.rollback()
                finally:
                    db.close()
                
                return result
                
            except Exception as e:
                logger.error(f"Ошибка в декораторе log_user_action для {action_type}: {e}")
                # Возвращаем исходную ошибку, не прерывая выполнение
                raise e
        
        return wrapper
    return decorator

def handle_errors(error_message: str = "❌ Произошла ошибка при выполнении команды."):
    """
    Декоратор для обработки ошибок с отправкой сообщения пользователю
    
    Args:
        error_message: Сообщение об ошибке для пользователя
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            try:
                return await func(update, context, *args, **kwargs)
            except Exception as e:
                logger.error(f"Ошибка в функции {func.__name__}: {e}")
                
                try:
                    if update.message:
                        await update.message.reply_text(error_message)
                    elif update.callback_query:
                        await update.callback_query.answer(error_message, show_alert=True)
                except Exception as send_error:
                    logger.error(f"Ошибка при отправке сообщения об ошибке: {send_error}")
        
        return wrapper
    return decorator

def current_time():
    """Получение текущего времени для использования в декораторах"""
    from datetime import datetime
    return datetime.utcnow()
