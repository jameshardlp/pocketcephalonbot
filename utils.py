import secrets
import re
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin

# Конфигурация
WIDGET_BASE_URL = "https://pocketcephalonbot-production.up.railway.app"  # Замените на реальный URL
TELEGRAM_BOT_USERNAME = "Pocketcephalonbot"  # Имя бота без @

def generate_widget_token() -> str:
    """Генерация токена для виджета"""
    return secrets.token_urlsafe(32)

def create_widget_url(token: str, base_url: Optional[str] = None) -> str:
    """Создание URL для виджета"""
    base = base_url or WIDGET_BASE_URL
    return f"{base.rstrip('/')}/?token={token}"

def create_telegram_bot_url() -> str:
    """Создание URL для открытия бота в Telegram"""
    return f"https://t.me/{TELEGRAM_BOT_USERNAME}"

def parse_time(time_str: str) -> Optional[datetime]:
    """
    Парсинг времени из API Warframe.
    Поддерживает форматы: ISO, с Z, с +00:00
    """
    if not time_str:
        return None
    
    try:
        # Удаляем пробелы и заменяем Z на +00:00 если нужно
        cleaned = time_str.strip().replace('Z', '+00:00')
        return datetime.fromisoformat(cleaned)
    except ValueError:
        try:
            # Пробуем альтернативные форматы
            for fmt in ['%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S%z']:
                try:
                    return datetime.strptime(time_str, fmt)
                except ValueError:
                    continue
        except Exception:
            pass
    
    return None

def format_time_remaining(time_str: str) -> str:
    """Форматирование оставшегося времени в человекочитаемый вид"""
    target = parse_time(time_str)
    if not target:
        return "Неизвестно"
    
    now = datetime.utcnow()
    
    # Если время уже прошло
    if target <= now:
        return "Завершено"
    
    diff = target - now
    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    seconds = diff.seconds % 60
    
    if days > 0:
        return f"{days}д {hours}ч {minutes}м"
    elif hours > 0:
        return f"{hours}ч {minutes}м"
    elif minutes > 0:
        return f"{minutes}м {seconds}с"
    else:
        return f"{seconds}с"

def format_datetime(dt: Optional[datetime], format_str: str = "%d.%m.%Y %H:%M") -> str:
    """Форматирование datetime в строку"""
    if not dt:
        return "Неизвестно"
    try:
        return dt.strftime(format_str)
    except Exception:
        return str(dt)

def format_credits(amount: int) -> str:
    """
    Форматирование кредитов в сокращенный вид
    1,000,000 -> 1.0M
    1,000 -> 1.0K
    """
    if amount >= 1_000_000:
        return f"{amount/1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"{amount/1_000:.1f}K"
    else:
        return str(amount)

def format_ducats(amount: int) -> str:
    """Форматирование дукатов"""
    return f"{amount:,}".replace(',', ' ')

def get_mission_recommendations(mission_type: str) -> List[str]:
    """Получение рекомендаций для миссии на основе типа"""
    recommendations = {
        'выживание': ['Танк', 'Поддержка', 'Контроль толпы'],
        'захват': ['Быстрый фрейм', 'Дальний бой', 'Мобильность'],
        'оборона': ['Контроль толпы', 'Высокий урон', 'Защита'],
        'разрушение': ['Высокий урон', 'Мобильность', 'Скорость'],
        'мобильная оборона': ['Контроль толпы', 'Защита', 'Поддержка'],
        'интерцепция': ['Контроль толпы', 'Мобильность', 'Скорость'],
        'экскавация': ['Защита', 'Поддержка', 'Контроль толпы'],
        'убийство': ['Высокий урон', 'Танк', 'Критические удары'],
        'шпионаж': ['Скорость', 'Невидимость', 'Мобильность']
    }
    
    for key, recs in recommendations.items():
        if key in mission_type.lower():
            return recs
    return ['Сбалансированная сборка']

def validate_telegram_id(telegram_id: int) -> bool:
    """Проверка валидности Telegram ID"""
    return isinstance(telegram_id, int) and telegram_id > 0

def validate_token(token: Optional[str]) -> bool:
    """Проверка валидности токена виджета"""
    if not token or not isinstance(token, str):
        return False
    # Токен должен быть длиной 32-64 символа и содержать только безопасные символы
    return 32 <= len(token) <= 64 and re.match(r'^[A-Za-z0-9_-]+$', token) is not None

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
        'nightwave': '🌙',
        'special_reactor': '⚡',
        'special_catalyst': '🔧'
    }
    return emojis.get(event_type, '📢')

def truncate_text(text: str, max_length: int = 500, suffix: str = '...') -> str:
    """
    Обрезка текста до определенной длины с добавлением суффикса
    """
    if not text:
        return ''
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def extract_mission_info(text: str) -> Dict[str, str]:
    """
    Извлечение информации о миссии из строки
    Пример: "1300 • Survival - Infestation @ Piscinas, Saturn (20% resource bonus)"
    """
    result = {
        'time': '',
        'type': '',
        'faction': '',
        'node': '',
        'planet': '',
        'bonus': ''
    }
    
    if not text or '|' not in text:
        return result
    
    parts = text.split(' | ', 1)
    if len(parts) == 2:
        result['time'] = parts[0].strip()
        details = parts[1].strip()
        
        # Парсим детали
        if ' @ ' in details:
            left, right = details.split(' @ ', 1)
            
            # Извлекаем тип и фракцию
            type_parts = left.split(' - ')
            if len(type_parts) == 2:
                result['type'] = type_parts[0].strip()
                result['faction'] = type_parts[1].strip()
            else:
                result['type'] = left.strip()
            
            # Извлекаем узел, планету и бонус
            if ' (' in right:
                node_planet, bonus = right.split(' (', 1)
                result['bonus'] = bonus.rstrip(')')
            else:
                node_planet = right
            
            if ', ' in node_planet:
                result['node'], result['planet'] = node_planet.split(', ', 1)
            else:
                result['node'] = node_planet
    
    return result

def safe_json_loads(data: Optional[str], default: Any = None) -> Any:
    """Безопасная загрузка JSON с обработкой ошибок"""
    if not data:
        return default
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(data: Any, default: str = '{}') -> str:
    """Безопасная выгрузка в JSON с обработкой ошибок"""
    try:
        return json.dumps(data, ensure_ascii=False, default=str)
    except Exception:
        return default

def is_valid_url(url: str) -> bool:
    """Проверка валидности URL"""
    if not url:
        return False
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])
    except Exception:
        return False
