"""
Сервис для работы с аналитикой и статистикой
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, case, cast, Date
from models import User, Post, UserActivity, Analytics, PostTemplate
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def log_user_activity(self, user_id: int, activity_type: str, 
                         activity_data: dict = None) -> UserActivity:
        """Логирование активности пользователя"""
        try:
            activity = UserActivity(
                user_id=user_id,
                activity_type=activity_type,
                activity_data=activity_data,
                timestamp=datetime.utcnow()
            )
            
            self.db.add(activity)
            self.db.flush()
            
            return activity
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def save_metric(self, metric_name: str, metric_value: int, 
                   metric_data: dict = None) -> Analytics:
        """Сохранение метрики в аналитику"""
        try:
            analytics = Analytics(
                metric_name=metric_name,
                metric_value=metric_value,
                metric_data=metric_data,
                date=datetime.utcnow()
            )
            
            self.db.add(analytics)
            self.db.flush()
            
            return analytics
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_basic_analytics(self) -> Dict[str, Any]:
        """Получение базовой аналитики"""
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        
        # Основные показатели
        total_users = self.db.query(User).count()
        total_posts = self.db.query(Post).filter(Post.is_deleted == False).count()
        published_posts = self.db.query(Post).filter(
            and_(Post.is_published == True, Post.is_deleted == False)
        ).count()
        
        # Активные пользователи за неделю
        weekly_active_users = self.db.query(User).filter(
            and_(
                User.last_activity >= week_ago,
                User.is_active == True
            )
        ).count()
        
        # Новые пользователи за неделю
        new_users_week = self.db.query(User).filter(
            User.created_at >= week_ago
        ).count()
        
        # Новые посты за неделю
        new_posts_week = self.db.query(Post).filter(
            and_(
                Post.created_at >= week_ago,
                Post.is_deleted == False
            )
        ).count()
        
        # Активности за неделю
        user_activities_week = self.db.query(UserActivity).filter(
            UserActivity.timestamp >= week_ago
        ).count()
        
        # Конверсия в публикацию
        draft_posts = self.db.query(Post).filter(
            and_(Post.is_published == False, Post.is_deleted == False)
        ).count()
        publication_rate = (published_posts / total_posts * 100) if total_posts > 0 else 0
        
        # Среднее постов на пользователя
        avg_posts_per_user = total_posts / total_users if total_users > 0 else 0
        
        # Активность пользователей
        user_activity_rate = (weekly_active_users / total_users * 100) if total_users > 0 else 0
        
        return {
            'total_users': total_users,
            'total_posts': total_posts,
            'published_posts': published_posts,
            'weekly_active_users': weekly_active_users,
            'new_users_week': new_users_week,
            'new_posts_week': new_posts_week,
            'user_activities_week': user_activities_week,
            'publication_rate': round(publication_rate, 1),
            'avg_posts_per_user': round(avg_posts_per_user, 1),
            'user_activity_rate': round(user_activity_rate, 1)
        }
    
    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики пользователя"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        
        # Активности пользователя
        total_activities = self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id
        ).count()
        
        weekly_activities = self.db.query(UserActivity).filter(
            and_(
                UserActivity.user_id == user_id,
                UserActivity.timestamp >= week_ago
            )
        ).count()
        
        # Посты пользователя
        user_posts = self.db.query(Post).filter(
            and_(Post.author_id == user_id, Post.is_deleted == False)
        ).all()
        
        total_posts = len(user_posts)
        published_posts = len([p for p in user_posts if p.is_published])
        draft_posts = total_posts - published_posts
        
        # Используемые шаблоны
        used_templates = list(set([p.template_type for p in user_posts if p.template_type]))
        
        return {
            'total_activities': total_activities,
            'weekly_activities': weekly_activities,
            'total_posts': total_posts,
            'published_posts': published_posts,
            'draft_posts': draft_posts,
            'used_templates': used_templates,
            'days_since_registration': (now - user.created_at).days,
            'last_activity': user.last_activity
        }
    
    def get_detailed_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Получение детальной статистики пользователя"""
        basic_stats = self.get_user_statistics(user_id)
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return basic_stats
        
        now = datetime.utcnow()
        month_ago = now - timedelta(days=30)
        
        # Активность за месяц
        monthly_activities = self.db.query(UserActivity).filter(
            and_(
                UserActivity.user_id == user_id,
                UserActivity.timestamp >= month_ago
            )
        ).count()
        
        # Средняя активность в день
        days_active = (now - user.created_at).days or 1
        avg_daily_activities = basic_stats['total_activities'] / days_active
        
        # Любимый шаблон
        template_usage = self.db.query(
            Post.template_type,
            func.count(Post.id).label('count')
        ).filter(
            and_(
                Post.author_id == user_id,
                Post.template_type.isnot(None),
                Post.is_deleted == False
            )
        ).group_by(Post.template_type).order_by(desc('count')).first()
        
        favorite_template = template_usage.template_type if template_usage else None
        
        # Ранг активности среди всех пользователей
        user_activities_count = basic_stats['total_activities']
        users_with_less_activity = self.db.query(User).join(UserActivity).group_by(
            User.id
        ).having(func.count(UserActivity.id) < user_activities_count).count()
        
        total_users = self.db.query(User).count()
        activity_rank = total_users - users_with_less_activity if total_users > 0 else 1
        
        # Процентиль публикаций
        publication_rate = (basic_stats['published_posts'] / basic_stats['total_posts'] * 100) \
                          if basic_stats['total_posts'] > 0 else 0
        
        users_with_lower_rate = self.db.query(User).join(Post).group_by(User.id).having(
            (func.sum(case((Post.is_published == True, 1), else_=0)) / 
             func.count(Post.id) * 100) < publication_rate
        ).count()
        
        publication_percentile = (users_with_lower_rate / total_users * 100) if total_users > 0 else 0
        
        return {
            **basic_stats,
            'monthly_activities': monthly_activities,
            'avg_daily_activities': round(avg_daily_activities, 1),
            'favorite_template': favorite_template,
            'activity_rank': activity_rank,
            'publication_percentile': round(publication_percentile, 1)
        }
    
    def get_post_statistics(self) -> Dict[str, Any]:
        """Получение статистики постов"""
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Основные показатели
        total_posts = self.db.query(Post).filter(Post.is_deleted == False).count()
        published_posts = self.db.query(Post).filter(
            and_(Post.is_published == True, Post.is_deleted == False)
        ).count()
        draft_posts = self.db.query(Post).filter(
            and_(Post.is_published == False, Post.is_deleted == False)
        ).count()
        deleted_posts = self.db.query(Post).filter(Post.is_deleted == True).count()
        
        # Динамика
        posts_this_week = self.db.query(Post).filter(
            and_(
                Post.created_at >= week_ago,
                Post.is_deleted == False
            )
        ).count()
        
        posts_this_month = self.db.query(Post).filter(
            and_(
                Post.created_at >= month_ago,
                Post.is_deleted == False
            )
        ).count()
        
        # Среднее в день
        days_since_first_post = 1
        first_post = self.db.query(Post).order_by(Post.created_at).first()
        if first_post:
            days_since_first_post = max((now - first_post.created_at).days, 1)
        
        avg_posts_per_day = total_posts / days_since_first_post
        
        # Самый активный автор
        most_active_author_result = self.db.query(
            User.first_name,
            User.username,
            func.count(Post.id).label('posts_count')
        ).join(Post).filter(
            Post.is_deleted == False
        ).group_by(User.id).order_by(desc('posts_count')).first()
        
        most_active_author = None
        if most_active_author_result:
            most_active_author = (most_active_author_result.first_name or 
                                 most_active_author_result.username or 'Unknown')
        
        # Средняя длина поста
        avg_length_result = self.db.query(
            func.avg(func.length(Post.content))
        ).filter(Post.is_deleted == False).scalar()
        
        avg_post_length = int(avg_length_result) if avg_length_result else 0
        
        # Самый популярный пост (по номеру - условно)
        most_popular_post = self.db.query(Post).filter(
            and_(Post.is_published == True, Post.is_deleted == False)
        ).order_by(desc(Post.published_at)).first()
        
        most_popular_post_number = most_popular_post.post_number if most_popular_post else None
        
        return {
            'total_posts': total_posts,
            'published_posts': published_posts,
            'draft_posts': draft_posts,
            'deleted_posts': deleted_posts,
            'posts_this_week': posts_this_week,
            'posts_this_month': posts_this_month,
            'avg_posts_per_day': round(avg_posts_per_day, 1),
            'most_active_author': most_active_author,
            'avg_post_length': avg_post_length,
            'most_popular_post': most_popular_post_number
        }
    
    def get_popular_templates(self) -> List[Dict[str, Any]]:
        """Получение популярных шаблонов"""
        results = self.db.query(
            Post.template_type,
            func.count(Post.id).label('usage_count')
        ).filter(
            and_(
                Post.template_type.isnot(None),
                Post.is_deleted == False
            )
        ).group_by(Post.template_type).order_by(desc('usage_count')).all()
        
        # Получение названий шаблонов из utils/templates.py
        from utils.templates import get_post_templates
        templates_info = {t['id']: t['name'] for t in get_post_templates()}
        
        return [
            {
                'id': result.template_type,
                'name': templates_info.get(result.template_type, result.template_type),
                'usage_count': result.usage_count
            }
            for result in results
        ]
    
    def get_template_usage_stats(self) -> List[Dict[str, Any]]:
        """Получение статистики использования шаблонов"""
        results = self.db.query(
            Post.template_type,
            func.count(Post.id).label('usage_count')
        ).filter(
            and_(
                Post.template_type.isnot(None),
                Post.is_deleted == False
            )
        ).group_by(Post.template_type).order_by(desc('usage_count')).all()
        
        # Получение названий шаблонов
        from utils.templates import get_post_templates
        templates_info = {t['id']: t['name'] for t in get_post_templates()}
        
        return [
            {
                'template_type': result.template_type,
                'template_name': templates_info.get(result.template_type, result.template_type),
                'usage_count': result.usage_count
            }
            for result in results
        ]
    
    def get_daily_statistics(self, days: int = 30) -> List[Dict[str, Any]]:
        """Получение ежедневной статистики"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Статистика активности пользователей
        user_activities = self.db.query(
            cast(UserActivity.timestamp, Date).label('date'),
            func.count(UserActivity.id).label('user_activities')
        ).filter(
            UserActivity.timestamp >= cutoff_date
        ).group_by(cast(UserActivity.timestamp, Date)).subquery()
        
        # Статистика создания постов
        post_creations = self.db.query(
            cast(Post.created_at, Date).label('date'),
            func.count(Post.id).label('posts_created')
        ).filter(
            and_(
                Post.created_at >= cutoff_date,
                Post.is_deleted == False
            )
        ).group_by(cast(Post.created_at, Date)).subquery()
        
        # Статистика новых пользователей
        new_users = self.db.query(
            cast(User.created_at, Date).label('date'),
            func.count(User.id).label('new_users')
        ).filter(
            User.created_at >= cutoff_date
        ).group_by(cast(User.created_at, Date)).subquery()
        
        # Объединение всех статистик
        # Создаем список дат
        date_list = []
        current_date = cutoff_date.date()
        end_date = datetime.utcnow().date()
        
        while current_date <= end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)
        
        # Получаем данные из подзапросов
        user_activity_data = {
            row.date: row.user_activities for row in self.db.query(user_activities).all()
        }
        post_creation_data = {
            row.date: row.posts_created for row in self.db.query(post_creations).all()
        }
        new_user_data = {
            row.date: row.new_users for row in self.db.query(new_users).all()
        }
        
        # Формируем итоговый список
        result = []
        for date in date_list:
            result.append({
                'date': date,
                'user_activities': user_activity_data.get(date, 0),
                'posts_created': post_creation_data.get(date, 0),
                'new_users': new_user_data.get(date, 0)
            })
        
        return result
    
    def get_admin_analytics(self) -> Dict[str, Any]:
        """Получение расширенной аналитики для администраторов"""
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # DAU, WAU, MAU
        daily_active_users = self.db.query(User).filter(
            and_(
                User.last_activity >= yesterday,
                User.is_active == True
            )
        ).count()
        
        weekly_active_users = self.db.query(User).filter(
            and_(
                User.last_activity >= week_ago,
                User.is_active == True
            )
        ).count()
        
        monthly_active_users = self.db.query(User).filter(
            and_(
                User.last_activity >= month_ago,
                User.is_active == True
            )
        ).count()
        
        # Retention Rate (пользователи, которые вернулись через неделю)
        week_old_users = self.db.query(User).filter(
            and_(
                User.created_at <= week_ago,
                User.created_at >= month_ago
            )
        ).count()
        
        retained_users = self.db.query(User).filter(
            and_(
                User.created_at <= week_ago,
                User.created_at >= month_ago,
                User.last_activity >= yesterday
            )
        ).count()
        
        retention_rate = (retained_users / week_old_users * 100) if week_old_users > 0 else 0
        
        # Конверсии
        total_users = self.db.query(User).count()
        users_with_posts = self.db.query(User).join(Post).filter(
            Post.is_deleted == False
        ).distinct().count()
        
        first_post_conversion = (users_with_posts / total_users * 100) if total_users > 0 else 0
        
        # Конверсия публикации
        total_posts = self.db.query(Post).filter(Post.is_deleted == False).count()
        published_posts = self.db.query(Post).filter(
            and_(Post.is_published == True, Post.is_deleted == False)
        ).count()
        
        publication_conversion = (published_posts / total_posts * 100) if total_posts > 0 else 0
        
        # Вовлеченность пользователей (среднее активностей на пользователя)
        total_activities = self.db.query(UserActivity).count()
        user_engagement = total_activities / total_users if total_users > 0 else 0
        
        # Производительность
        # Среднее время создания поста (условно - время между регистрацией и первым постом)
        avg_creation_time = "Менее часа"  # Упрощенная метрика
        
        # Пик активности (час)
        peak_activity_result = self.db.query(
            func.extract('hour', UserActivity.timestamp).label('hour'),
            func.count(UserActivity.id).label('count')
        ).group_by('hour').order_by(desc('count')).first()
        
        peak_activity_hour = int(peak_activity_result.hour) if peak_activity_result else 12
        
        # Самый продуктивный день недели
        most_productive_day_result = self.db.query(
            func.extract('dow', Post.created_at).label('dow'),
            func.count(Post.id).label('count')
        ).filter(
            Post.is_deleted == False
        ).group_by('dow').order_by(desc('count')).first()
        
        days_map = {0: 'Воскресенье', 1: 'Понедельник', 2: 'Вторник', 3: 'Среда', 
                   4: 'Четверг', 5: 'Пятница', 6: 'Суббота'}
        most_productive_day = days_map.get(
            int(most_productive_day_result.dow) if most_productive_day_result else 1, 
            'Понедельник'
        )
        
        # Тренды (рост за последний месяц vs предыдущий месяц)
        prev_month_start = month_ago - timedelta(days=30)
        
        current_month_users = self.db.query(User).filter(
            User.created_at >= month_ago
        ).count()
        
        prev_month_users = self.db.query(User).filter(
            and_(
                User.created_at >= prev_month_start,
                User.created_at < month_ago
            )
        ).count()
        
        user_growth_rate = ((current_month_users - prev_month_users) / prev_month_users * 100) \
                          if prev_month_users > 0 else 0
        
        current_month_posts = self.db.query(Post).filter(
            and_(
                Post.created_at >= month_ago,
                Post.is_deleted == False
            )
        ).count()
        
        prev_month_posts = self.db.query(Post).filter(
            and_(
                Post.created_at >= prev_month_start,
                Post.created_at < month_ago,
                Post.is_deleted == False
            )
        ).count()
        
        post_growth_rate = ((current_month_posts - prev_month_posts) / prev_month_posts * 100) \
                          if prev_month_posts > 0 else 0
        
        current_month_activities = self.db.query(UserActivity).filter(
            UserActivity.timestamp >= month_ago
        ).count()
        
        prev_month_activities = self.db.query(UserActivity).filter(
            and_(
                UserActivity.timestamp >= prev_month_start,
                UserActivity.timestamp < month_ago
            )
        ).count()
        
        activity_change = ((current_month_activities - prev_month_activities) / prev_month_activities * 100) \
                         if prev_month_activities > 0 else 0
        
        return {
            'daily_active_users': daily_active_users,
            'weekly_active_users': weekly_active_users,
            'monthly_active_users': monthly_active_users,
            'retention_rate': round(retention_rate, 1),
            'first_post_conversion': round(first_post_conversion, 1),
            'publication_conversion': round(publication_conversion, 1),
            'user_engagement': round(user_engagement, 1),
            'avg_post_creation_time': avg_creation_time,
            'peak_activity_hour': peak_activity_hour,
            'most_productive_day': most_productive_day,
            'user_growth_rate': round(user_growth_rate, 1),
            'post_growth_rate': round(post_growth_rate, 1),
            'activity_change': round(activity_change, 1)
        }
    
    def export_users_data(self) -> List[Dict[str, Any]]:
        """Экспорт данных пользователей"""
        users = self.db.query(User).all()
        
        users_data = []
        for user in users:
            posts_count = len([p for p in user.posts if not p.is_deleted])
            published_posts = len([p for p in user.posts if p.is_published and not p.is_deleted])
            activities_count = len(user.activities)
            
            users_data.append({
                'user_id': user.id,
                'telegram_id': user.telegram_id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_admin': user.is_admin,
                'is_active': user.is_active,
                'created_at': user.created_at,
                'updated_at': user.updated_at,
                'last_activity': user.last_activity,
                'posts_count': posts_count,
                'published_posts': published_posts,
                'activities_count': activities_count
            })
        
        return users_data
    
    def export_posts_data(self) -> List[Dict[str, Any]]:
        """Экспорт данных постов"""
        posts = self.db.query(Post).filter(Post.is_deleted == False).all()
        
        posts_data = []
        for post in posts:
            posts_data.append({
                'post_id': post.id,
                'post_number': post.post_number,
                'title': post.title,
                'content': post.content,
                'template_type': post.template_type,
                'is_published': post.is_published,
                'author_id': post.author_id,
                'author_name': post.author.first_name or post.author.username,
                'created_at': post.created_at,
                'updated_at': post.updated_at,
                'published_at': post.published_at,
                'content_length': len(post.content)
            })
        
        return posts_data
    
    def export_analytics_data(self) -> List[Dict[str, Any]]:
        """Экспорт аналитических данных"""
        analytics = self.db.query(Analytics).order_by(desc(Analytics.date)).all()
        
        analytics_data = []
        for analytic in analytics:
            analytics_data.append({
                'id': analytic.id,
                'metric_name': analytic.metric_name,
                'metric_value': analytic.metric_value,
                'metric_data': analytic.metric_data,
                'date': analytic.date
            })
        
        return analytics_data
