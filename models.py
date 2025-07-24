"""
Модели базы данных
"""

from sqlalchemy import Column, Integer, BigInteger, String, Text, Boolean, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"

class Post(Base):
    """Модель поста"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    post_number = Column(Integer, unique=True, index=True, nullable=False)  # Глобальная нумерация
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    template_type = Column(String(100), nullable=True)  # Тип использованного шаблона
    is_published = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Связи
    author = relationship("User", back_populates="posts")
    
    # Индексы
    __table_args__ = (
        Index('idx_post_author_created', 'author_id', 'created_at'),
        Index('idx_post_published', 'is_published', 'published_at'),
    )
    
    def __repr__(self):
        return f"<Post(post_number={self.post_number}, title={self.title[:50]})>"

class PostTemplate(Base):
    """Модель шаблона поста"""
    __tablename__ = "post_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    template_fields = Column(JSON, nullable=False)  # Структура полей шаблона
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<PostTemplate(name={self.name})>"

class UserActivity(Base):
    """Модель активности пользователя"""
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String(100), nullable=False)  # 'command', 'post_create', 'post_edit', etc.
    activity_data = Column(JSON, nullable=True)  # Дополнительные данные о действии
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    user = relationship("User", back_populates="activities")
    
    # Индексы
    __table_args__ = (
        Index('idx_activity_user_time', 'user_id', 'timestamp'),
        Index('idx_activity_type_time', 'activity_type', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<UserActivity(user_id={self.user_id}, type={self.activity_type})>"

class Analytics(Base):
    """Модель аналитики"""
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(200), nullable=False)
    metric_value = Column(Integer, nullable=False)
    metric_data = Column(JSON, nullable=True)  # Дополнительные данные метрики
    date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Индексы
    __table_args__ = (
        Index('idx_analytics_metric_date', 'metric_name', 'date'),
    )
    
    def __repr__(self):
        return f"<Analytics(metric={self.metric_name}, value={self.metric_value})>"
