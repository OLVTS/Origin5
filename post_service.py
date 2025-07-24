"""
Сервис для работы с постами
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from models import Post, User
from datetime import datetime
from typing import List, Optional

class PostService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_post(self, title: str, content: str, author_id: int, template_type: str = None) -> Post:
        """Создание нового поста"""
        try:
            # Получение следующего номера поста
            last_post = self.db.query(Post).order_by(desc(Post.post_number)).first()
            next_number = (last_post.post_number + 1) if last_post else 1
            
            post = Post(
                post_number=next_number,
                title=title,
                content=content,
                author_id=author_id,
                template_type=template_type,
                is_published=False,
                is_deleted=False
            )
            
            self.db.add(post)
            self.db.flush()  # Получить ID без коммита
            
            return post
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        """Получение поста по ID"""
        return self.db.query(Post).filter(
            and_(Post.id == post_id, Post.is_deleted == False)
        ).first()
    
    def get_post_by_number(self, post_number: int) -> Optional[Post]:
        """Получение поста по номеру"""
        return self.db.query(Post).filter(
            and_(Post.post_number == post_number, Post.is_deleted == False)
        ).first()
    
    def get_user_posts(self, user_id: int, include_deleted: bool = False) -> List[Post]:
        """Получение постов пользователя"""
        query = self.db.query(Post).filter(Post.author_id == user_id)
        
        if not include_deleted:
            query = query.filter(Post.is_deleted == False)
        
        return query.order_by(desc(Post.created_at)).all()
    
    def get_published_posts(self, limit: int = 50) -> List[Post]:
        """Получение опубликованных постов"""
        return self.db.query(Post).filter(
            and_(
                Post.is_published == True,
                Post.is_deleted == False
            )
        ).order_by(desc(Post.published_at)).limit(limit).all()
    
    def get_unpublished_posts(self, limit: int = 50) -> List[Post]:
        """Получение неопубликованных постов"""
        return self.db.query(Post).filter(
            and_(
                Post.is_published == False,
                Post.is_deleted == False
            )
        ).order_by(desc(Post.created_at)).limit(limit).all()
    
    def get_recent_posts(self, limit: int = 20) -> List[Post]:
        """Получение последних постов"""
        return self.db.query(Post).filter(
            Post.is_deleted == False
        ).order_by(desc(Post.created_at)).limit(limit).all()
    
    def update_post(self, post_id: int, title: str = None, content: str = None) -> bool:
        """Обновление поста"""
        try:
            post = self.get_post_by_id(post_id)
            if not post:
                return False
            
            if title is not None:
                post.title = title
            if content is not None:
                post.content = content
            
            post.updated_at = datetime.utcnow()
            
            return True
            
        except Exception:
            self.db.rollback()
            return False
    
    def toggle_post_publication(self, post_number: int) -> bool:
        """Переключение статуса публикации поста"""
        try:
            post = self.get_post_by_number(post_number)
            if not post:
                return False
            
            post.is_published = not post.is_published
            
            if post.is_published:
                post.published_at = datetime.utcnow()
            else:
                post.published_at = None
            
            return True
            
        except Exception:
            self.db.rollback()
            return False
    
    def delete_post(self, post_number: int, hard_delete: bool = False) -> bool:
        """Удаление поста"""
        try:
            post = self.get_post_by_number(post_number)
            if not post:
                return False
            
            if hard_delete:
                self.db.delete(post)
            else:
                post.is_deleted = True
                post.updated_at = datetime.utcnow()
            
            return True
            
        except Exception:
            self.db.rollback()
            return False
    
    def search_posts(self, query: str, limit: int = 20) -> List[Post]:
        """Поиск постов по тексту"""
        search_term = f"%{query}%"
        return self.db.query(Post).filter(
            and_(
                Post.is_deleted == False,
                Post.is_published == True,
                (Post.title.ilike(search_term) | Post.content.ilike(search_term))
            )
        ).order_by(desc(Post.published_at)).limit(limit).all()
    
    def get_posts_by_template(self, template_type: str) -> List[Post]:
        """Получение постов по типу шаблона"""
        return self.db.query(Post).filter(
            and_(
                Post.template_type == template_type,
                Post.is_deleted == False
            )
        ).order_by(desc(Post.created_at)).all()
    
    def get_posts_count(self) -> int:
        """Получение общего количества постов"""
        return self.db.query(Post).filter(Post.is_deleted == False).count()
    
    def get_published_posts_count(self) -> int:
        """Получение количества опубликованных постов"""
        return self.db.query(Post).filter(
            and_(Post.is_published == True, Post.is_deleted == False)
        ).count()
    
    def get_draft_posts_count(self) -> int:
        """Получение количества черновиков"""
        return self.db.query(Post).filter(
            and_(Post.is_published == False, Post.is_deleted == False)
        ).count()
    
    def get_posts_by_author_count(self, author_id: int) -> int:
        """Получение количества постов автора"""
        return self.db.query(Post).filter(
            and_(Post.author_id == author_id, Post.is_deleted == False)
        ).count()
    
    def get_top_authors(self, limit: int = 10) -> List[dict]:
        """Получение топ авторов по количеству постов"""
        results = self.db.query(
            User.id,
            User.first_name,
            User.username,
            func.count(Post.id).label('posts_count')
        ).join(Post).filter(
            Post.is_deleted == False
        ).group_by(User.id).order_by(
            desc('posts_count')
        ).limit(limit).all()
        
        return [
            {
                'user_id': result.id,
                'name': result.first_name or result.username or f'User {result.id}',
                'posts_count': result.posts_count
            }
            for result in results
        ]
    
    def get_template_usage_stats(self) -> List[dict]:
        """Получение статистики использования шаблонов"""
        results = self.db.query(
            Post.template_type,
            func.count(Post.id).label('usage_count')
        ).filter(
            and_(Post.template_type.isnot(None), Post.is_deleted == False)
        ).group_by(Post.template_type).order_by(
            desc('usage_count')
        ).all()
        
        return [
            {
                'template_type': result.template_type,
                'usage_count': result.usage_count
            }
            for result in results
        ]
    
    def get_posts_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Post]:
        """Получение постов за период"""
        return self.db.query(Post).filter(
            and_(
                Post.created_at >= start_date,
                Post.created_at <= end_date,
                Post.is_deleted == False
            )
        ).order_by(desc(Post.created_at)).all()
    
    def get_daily_posts_stats(self, days: int = 30) -> List[dict]:
        """Получение ежедневной статистики постов"""
        from sqlalchemy import Date, cast
        
        results = self.db.query(
            cast(Post.created_at, Date).label('date'),
            func.count(Post.id).label('posts_count'),
            func.sum(func.case((Post.is_published == True, 1), else_=0)).label('published_count')
        ).filter(
            and_(
                Post.created_at >= datetime.utcnow() - timedelta(days=days),
                Post.is_deleted == False
            )
        ).group_by(cast(Post.created_at, Date)).order_by('date').all()
        
        return [
            {
                'date': result.date,
                'posts_count': result.posts_count,
                'published_count': result.published_count or 0
            }
            for result in results
        ]
