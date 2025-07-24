"""
Сервис для работы с пользователями
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from models import User, UserActivity
from datetime import datetime, timedelta
from typing import List, Optional

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_or_update_user(self, telegram_id: int, username: str = None, 
                             first_name: str = None, last_name: str = None,
                             is_admin: bool = False) -> User:
        """Создание или обновление пользователя"""
        try:
            # Поиск существующего пользователя
            user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
            
            if user:
                # Обновление существующего пользователя
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                user.last_activity = datetime.utcnow()
                user.updated_at = datetime.utcnow()
                
                # Обновляем is_admin только если явно указано
                if is_admin and not user.is_admin:
                    user.is_admin = is_admin
            else:
                # Создание нового пользователя
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    is_admin=is_admin,
                    is_active=True,
                    last_activity=datetime.utcnow()
                )
                self.db.add(user)
            
            self.db.flush()  # Получить ID без коммита
            return user
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получение пользователя по Telegram ID"""
        return self.db.query(User).filter(User.telegram_id == telegram_id).first()
    
    def get_all_users(self, limit: int = 100, include_inactive: bool = True) -> List[User]:
        """Получение всех пользователей"""
        query = self.db.query(User)
        
        if not include_inactive:
            query = query.filter(User.is_active == True)
        
        return query.order_by(desc(User.created_at)).limit(limit).all()
    
    def get_users_count(self) -> int:
        """Получение общего количества пользователей"""
        return self.db.query(User).count()
    
    def get_active_users_count(self, days: int = 7) -> int:
        """Получение количества активных пользователей за период"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(User).filter(
            and_(
                User.last_activity >= cutoff_date,
                User.is_active == True
            )
        ).count()
    
    def get_admin_users(self) -> List[User]:
        """Получение списка администраторов"""
        return self.db.query(User).filter(
            and_(User.is_admin == True, User.is_active == True)
        ).all()
    
    def promote_to_admin(self, telegram_id: int) -> bool:
        """Назначение пользователя администратором"""
        try:
            user = self.get_user_by_telegram_id(telegram_id)
            if not user:
                return False
            
            user.is_admin = True
            user.updated_at = datetime.utcnow()
            
            return True
            
        except Exception:
            self.db.rollback()
            return False
    
    def demote_from_admin(self, telegram_id: int) -> bool:
        """Снятие прав администратора"""
        try:
            user = self.get_user_by_telegram_id(telegram_id)
            if not user:
                return False
            
            user.is_admin = False
            user.updated_at = datetime.utcnow()
            
            return True
            
        except Exception:
            self.db.rollback()
            return False
    
    def toggle_user_status(self, telegram_id: int) -> bool:
        """Переключение статуса активности пользователя"""
        try:
            user = self.get_user_by_telegram_id(telegram_id)
            if not user:
                return False
            
            user.is_active = not user.is_active
            user.updated_at = datetime.utcnow()
            
            return True
            
        except Exception:
            self.db.rollback()
            return False
    
    def block_user(self, telegram_id: int) -> bool:
        """Блокировка пользователя"""
        try:
            user = self.get_user_by_telegram_id(telegram_id)
            if not user:
                return False
            
            user.is_active = False
            user.updated_at = datetime.utcnow()
            
            return True
            
        except Exception:
            self.db.rollback()
            return False
    
    def unblock_user(self, telegram_id: int) -> bool:
        """Разблокировка пользователя"""
        try:
            user = self.get_user_by_telegram_id(telegram_id)
            if not user:
                return False
            
            user.is_active = True
            user.updated_at = datetime.utcnow()
            
            return True
            
        except Exception:
            self.db.rollback()
            return False
    
    def update_last_activity(self, telegram_id: int) -> bool:
        """Обновление времени последней активности"""
        try:
            user = self.get_user_by_telegram_id(telegram_id)
            if not user:
                return False
            
            user.last_activity = datetime.utcnow()
            
            return True
            
        except Exception:
            self.db.rollback()
            return False
    
    def get_user_statistics(self, user_id: int) -> dict:
        """Получение статистики пользователя"""
        user = self.get_user_by_id(user_id)
        if not user:
            return {}
        
        # Основная статистика
        total_posts = len([p for p in user.posts if not p.is_deleted])
        published_posts = len([p for p in user.posts if p.is_published and not p.is_deleted])
        draft_posts = total_posts - published_posts
        
        # Активность
        total_activities = len(user.activities)
        
        # Активность за неделю
        week_ago = datetime.utcnow() - timedelta(days=7)
        weekly_activities = len([a for a in user.activities if a.timestamp >= week_ago])
        
        # Дни в системе
        days_since_registration = (datetime.utcnow() - user.created_at).days
        
        return {
            'total_posts': total_posts,
            'published_posts': published_posts,
            'draft_posts': draft_posts,
            'total_activities': total_activities,
            'weekly_activities': weekly_activities,
            'days_since_registration': days_since_registration,
            'registration_date': user.created_at,
            'last_activity': user.last_activity,
            'is_admin': user.is_admin,
            'is_active': user.is_active
        }
    
    def get_new_users_count(self, days: int = 7) -> int:
        """Получение количества новых пользователей за период"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(User).filter(User.created_at >= cutoff_date).count()
    
    def get_users_by_activity_level(self, min_posts: int = 1) -> List[User]:
        """Получение пользователей по уровню активности"""
        users = self.db.query(User).filter(User.is_active == True).all()
        
        active_users = []
        for user in users:
            posts_count = len([p for p in user.posts if not p.is_deleted])
            if posts_count >= min_posts:
                active_users.append(user)
        
        return sorted(active_users, key=lambda u: len(u.posts), reverse=True)
    
    def search_users(self, query: str) -> List[User]:
        """Поиск пользователей по имени или username"""
        search_term = f"%{query}%"
        return self.db.query(User).filter(
            (User.first_name.ilike(search_term)) |
            (User.last_name.ilike(search_term)) |
            (User.username.ilike(search_term))
        ).filter(User.is_active == True).all()
    
    def get_user_activity_history(self, user_id: int, limit: int = 50) -> List[UserActivity]:
        """Получение истории активности пользователя"""
        return self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id
        ).order_by(desc(UserActivity.timestamp)).limit(limit).all()
    
    def get_top_active_users(self, limit: int = 10, days: int = 30) -> List[dict]:
        """Получение топ активных пользователей"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Подсчет активности пользователей
        results = self.db.query(
            User.id,
            User.first_name,
            User.username,
            func.count(UserActivity.id).label('activity_count')
        ).join(UserActivity).filter(
            and_(
                UserActivity.timestamp >= cutoff_date,
                User.is_active == True
            )
        ).group_by(User.id).order_by(
            desc('activity_count')
        ).limit(limit).all()
        
        return [
            {
                'user_id': result.id,
                'name': result.first_name or result.username or f'User {result.id}',
                'activity_count': result.activity_count
            }
            for result in results
        ]
    
    def get_user_registration_stats(self, days: int = 30) -> List[dict]:
        """Получение статистики регистраций по дням"""
        from sqlalchemy import Date, cast
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        results = self.db.query(
            cast(User.created_at, Date).label('date'),
            func.count(User.id).label('registrations')
        ).filter(
            User.created_at >= cutoff_date
        ).group_by(cast(User.created_at, Date)).order_by('date').all()
        
        return [
            {
                'date': result.date,
                'registrations': result.registrations
            }
            for result in results
        ]
    
    def is_user_admin(self, telegram_id: int) -> bool:
        """Проверка является ли пользователь администратором"""
        user = self.get_user_by_telegram_id(telegram_id)
        return user.is_admin if user else False
    
    def is_user_active(self, telegram_id: int) -> bool:
        """Проверка активности пользователя"""
        user = self.get_user_by_telegram_id(telegram_id)
        return user.is_active if user else False
