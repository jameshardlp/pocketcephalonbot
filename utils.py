import secrets
from datetime import datetime, timedelta
from typing import Optional

def generate_widget_token() -> str:
    """Генерация токена для виджета"""
    return secrets.token_urlsafe(32)

def create_widget_url(token: str) -> str:
    """Создание URL для виджета"""
    base_url = "https://ваш-railway-url.railway.app"
    return f"{base_url}?token={token}"

def parse_time(time_str: str) -> Optional[datetime]:
    """Парсинг времени из API Warframe"""
    try:
        return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
    except:
        return None

def format_time_remaining(time_str: str) -> str:
    """Форматирование оставшегося времени"""
    target = parse_time(time_str)
    if not target:
        return "Неизвестно"
    
    now = datetime.utcnow()
    diff = target - now
    
    if diff.total_seconds() <= 0:
        return "Завершено"
    
    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    
    if days > 0:
        return f"{days}д {hours}ч {minutes}м"
    elif hours > 0:
        return f"{hours}ч {minutes}м"
    else:
        return f"{minutes}м"

def format_credits(amount: int) -> str:
    """Форматирование кредитов"""
    if amount >= 1000000:
        return f"{amount/1000000:.1f}M"
    elif amount >= 1000:
        return f"{amount/1000:.1f}K"
    else:
        return str(amount)

def get_mission_recommendations(mission_type: str) -> list:
    """Получение рекомендаций для миссии"""
    recommendations = {
        'выживание': ['Танк', 'Поддержка', 'Контроль толпы'],
        'захват': ['Быстрый фрейм', 'Дальний бой'],
        'оборона': ['Контроль толпы', 'Высокий урон'],
        'разрушение': ['Высокий урон', 'Мобильность'],
        'мобильная оборона': ['Контроль толпы', 'Защита'],
        'интерцепция': ['Контроль толпы', 'Мобильность'],
        'экскавация': ['Защита', 'Поддержка']
    }
    
    for key, recs in recommendations.items():
        if key in mission_type.lower():
            return recs
    return ['Сбалансированная сборка']

def validate_telegram_id(telegram_id: int) -> bool:
    """Проверка валидности Telegram ID"""
    return isinstance(telegram_id, int) and telegram_id > 0

def get_emoji_for_event(event_type: str) -> str:
    """Получение эмодзи для типа события"""
    emojis = {
        'baro': '🧛',
        'fissures': '💠',
        'invasions': '⚔️',
        'sortie': '🎯',
        'arbitration': '⚡',
        'archon': '🔥',
        'steel_path': '🗡️',
        'alerts': '🚨',
        'earth_cycle': '🌍',
        'venus_weather': '🌡️',
        'deimos_cycle': '🕷️',
        'duviri_mood': '🎭',
        'ergo_glast': '🛒',
        'eleonora': '🛒',
        'special_reactor': '⚡',
        'special_catalyst': '🔧'
    }
    return emojis.get(event_type, '📢')

def truncate_text(text: str, max_length: int = 500) -> str:
    """Обрезка текста до определенной длины"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'