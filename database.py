from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, JSON, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import os
import secrets

from config import DATABASE_URL

# Настройка engine с улучшенными параметрами для продакшена
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=5,  # Максимальное количество соединений в пуле
    max_overflow=10,  # Дополнительные соединения при необходимости
    pool_timeout=30  # Таймаут ожидания соединения
)

Base = declarative_base()
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_notification = Column(DateTime)
    
    # Основные уведомления
    notify_baro = Column(Boolean, default=True)
    notify_fissures = Column(Boolean, default=True)
    notify_invasions = Column(Boolean, default=True)
    notify_sortie = Column(Boolean, default=True)
    notify_arbitration = Column(Boolean, default=True)
    notify_archon = Column(Boolean, default=True)
    notify_steel_path = Column(Boolean, default=True)
    notify_alerts = Column(Boolean, default=True)
    
    # Циклы и погода
    notify_earth_cycle = Column(Boolean, default=True)
    notify_venus_weather = Column(Boolean, default=True)
    notify_deimos_cycle = Column(Boolean, default=True)
    notify_duviri_mood = Column(Boolean, default=True)
    
    # Торговцы
    notify_ergo_glast = Column(Boolean, default=True)
    notify_cavalero = Column(Boolean, default=True)
    notify_eleonora = Column(Boolean, default=True)
    notify_nightwave = Column(Boolean, default=True)
    
    # Реакторы и катализаторы
    notify_reactor = Column(Boolean, default=True)
    notify_catalyst = Column(Boolean, default=True)
    
    # Дополнительные настройки
    custom_settings = Column(JSON, default=lambda: {})
    widget_token = Column(String(64), unique=True, nullable=True)
    
    # Индексы для ускорения запросов
    __table_args__ = (
        Index('idx_telegram_id', 'telegram_id'),
        Index('idx_widget_token', 'widget_token'),
    )
    
    def get_settings(self):
        if self.custom_settings is None:
            return {}
        return self.custom_settings
    
    def to_dict(self):
        """Преобразование пользователя в словарь для API"""
        return {
            'telegram_id': self.telegram_id,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'settings': {
                'baro': self.notify_baro,
                'fissures': self.notify_fissures,
                'invasions': self.notify_invasions,
                'sortie': self.notify_sortie,
                'arbitration': self.notify_arbitration,
                'archon': self.notify_archon,
                'steel_path': self.notify_steel_path,
                'alerts': self.notify_alerts,
                'earth_cycle': self.notify_earth_cycle,
                'venus_weather': self.notify_venus_weather,
                'deimos_cycle': self.notify_deimos_cycle,
                'duviri_mood': self.notify_duviri_mood,
                'nightwave': self.notify_nightwave,
                'reactor': self.notify_reactor,
                'catalyst': self.notify_catalyst
            }
        }

class NotificationQueue(Base):
    __tablename__ = 'notification_queue'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    notification_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)
    is_sent = Column(Boolean, default=False)
    
    # Индексы
    __table_args__ = (
        Index('idx_queue_user_id', 'user_id'),
        Index('idx_queue_is_sent', 'is_sent'),
        Index('idx_queue_created', 'created_at'),
    )

class NotificationHistory(Base):
    __tablename__ = 'notifications_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    notification_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    
    # Индексы
    __table_args__ = (
        Index('idx_history_user_id', 'user_id'),
        Index('idx_history_sent_at', 'sent_at'),
        Index('idx_history_type', 'notification_type'),
    )

def init_db():
    """Инициализация базы данных - создание всех таблиц"""
    try:
        Base.metadata.create_all(engine)
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        raise

def get_user(telegram_id):
    """Получение пользователя по telegram_id, создание при необходимости"""
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id)
            session.add(user)
            session.commit()
        return user
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_user_by_widget_token(widget_token):
    """Получение пользователя по токену виджета"""
    session = Session()
    try:
        return session.query(User).filter_by(widget_token=widget_token).first()
    finally:
        session.close()

def update_user_settings(telegram_id, **kwargs):
    """Обновление настроек пользователя"""
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id)
            session.add(user)
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        session.commit()
        return user
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def add_to_queue(telegram_id, notification_type, content):
    """Добавление уведомления в очередь"""
    session = Session()
    try:
        queue_item = NotificationQueue(
            user_id=telegram_id,
            notification_type=notification_type[:50],
            content=content
        )
        session.add(queue_item)
        session.commit()
        return queue_item.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_pending_notifications(limit=100):
    """Получение ожидающих уведомлений из очереди"""
    session = Session()
    try:
        return session.query(NotificationQueue)\
            .filter_by(is_sent=False)\
            .order_by(NotificationQueue.created_at)\
            .limit(limit)\
            .all()
    finally:
        session.close()

def mark_as_sent(notification_id):
    """Отметка уведомления как отправленного"""
    session = Session()
    try:
        notification = session.query(NotificationQueue)\
            .filter_by(id=notification_id)\
            .first()
        if notification:
            notification.is_sent = True
            notification.sent_at = datetime.utcnow()
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def save_history(telegram_id, notification_type, content):
    """Сохранение истории отправленных уведомлений"""
    session = Session()
    try:
        history = NotificationHistory(
            user_id=telegram_id,
            notification_type=notification_type[:50],
            content=content
        )
        session.add(history)
        session.commit()
        return history.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def generate_widget_token(telegram_id):
    """Генерация уникального токена для виджета"""
    token = secrets.token_urlsafe(32)
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            user.widget_token = token
            session.commit()
        return token
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def cleanup_old_history(days=30):
    """Очистка старой истории уведомлений"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    session = Session()
    try:
        deleted = session.query(NotificationHistory)\
            .filter(NotificationHistory.sent_at < cutoff_date)\
            .delete()
        session.commit()
        return deleted
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_user_count():
    """Получение количества пользователей"""
    session = Session()
    try:
        return session.query(User).count()
    finally:
        session.close()

def get_users_with_notification_enabled(notification_type):
    """Получение пользователей с включенным конкретным уведомлением"""
    session = Session()
    try:
        return session.query(User.telegram_id)\
            .filter(getattr(User, notification_type) == True)\
            .all()
    finally:
        session.close()
