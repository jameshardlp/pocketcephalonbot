from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import os

from config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600
)

Base = declarative_base()
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String)
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
    widget_token = Column(String, unique=True)
    
    def get_settings(self):
        if self.custom_settings is None:
            return {}
        return self.custom_settings

class NotificationQueue(Base):
    __tablename__ = 'notification_queue'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    notification_type = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)
    is_sent = Column(Boolean, default=False)

class NotificationHistory(Base):
    __tablename__ = 'notifications_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    notification_type = Column(String)
    content = Column(Text)
    sent_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    try:
        Base.metadata.create_all(engine)
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        raise

def get_user(telegram_id):
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id)
            session.add(user)
            session.commit()
        return user
    finally:
        session.close()

def update_user_settings(telegram_id, **kwargs):
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
    finally:
        session.close()

def add_to_queue(telegram_id, notification_type, content):
    session = Session()
    try:
        queue_item = NotificationQueue(
            user_id=telegram_id,
            notification_type=notification_type,
            content=content
        )
        session.add(queue_item)
        session.commit()
    finally:
        session.close()

def get_pending_notifications():
    session = Session()
    try:
        return session.query(NotificationQueue).filter_by(is_sent=False).order_by(NotificationQueue.created_at).all()
    finally:
        session.close()

def mark_as_sent(notification_id):
    session = Session()
    try:
        notification = session.query(NotificationQueue).filter_by(id=notification_id).first()
        if notification:
            notification.is_sent = True
            notification.sent_at = datetime.utcnow()
            session.commit()
    finally:
        session.close()

def save_history(telegram_id, notification_type, content):
    session = Session()
    try:
        history = NotificationHistory(
            user_id=telegram_id,
            notification_type=notification_type,
            content=content
        )
        session.add(history)
        session.commit()
    finally:
        session.close()

def generate_widget_token(telegram_id):
    import secrets
    token = secrets.token_urlsafe(32)
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            user.widget_token = token
            session.commit()
        return token
    finally:
        session.close()
