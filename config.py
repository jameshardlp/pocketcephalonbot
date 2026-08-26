import os
from dotenv import load_dotenv
from typing import Optional

# Загрузка переменных окружения
load_dotenv()

# --- Обязательные переменные ---
BOT_TOKEN: str = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is required! Please set it in .env file or environment variables.")

# --- База данных ---
DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///warframe_bot.db')

# --- Веб-сервер ---
WEB_PORT: int = int(os.getenv('WEB_PORT', 8000))
WEB_HOST: str = os.getenv('WEB_HOST', '0.0.0.0')
WEBHOOK_URL: Optional[str] = os.getenv('WEBHOOK_URL') or None

# --- Настройки бота ---
RATE_LIMIT: int = int(os.getenv('RATE_LIMIT', 5))  # Секунд между сообщениями
CHECK_INTERVAL: int = int(os.getenv('CHECK_INTERVAL', 30))  # Секунд между проверками
MAX_NOTIFICATIONS_PER_MINUTE: int = int(os.getenv('MAX_NOTIFICATIONS_PER_MINUTE', 20))
BATCH_SIZE: int = int(os.getenv('BATCH_SIZE', 10))  # Количество пользователей за одну отправку

# --- API ---
WARFRAME_API_URL: str = os.getenv('WARFRAME_API_URL', 'https://api.warframestat.us/pc')
WARFRAME_API_TIMEOUT: int = int(os.getenv('WARFRAME_API_TIMEOUT', 10))  # Таймаут в секундах

# --- API ключи (опционально) ---
API_KEY: Optional[str] = os.getenv('API_KEY') or None

# --- Виджет ---
WIDGET_BASE_URL: str = os.getenv('WIDGET_BASE_URL', 'https://ваш-railway-url.railway.app')
WIDGET_TOKEN_LENGTH: int = int(os.getenv('WIDGET_TOKEN_LENGTH', 32))

# --- Логирование ---
LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_FILE: Optional[str] = os.getenv('LOG_FILE') or None

# --- Очередь уведомлений ---
QUEUE_RETRY_DELAY: int = int(os.getenv('QUEUE_RETRY_DELAY', 60))  # Секунд до повторной попытки
QUEUE_MAX_RETRIES: int = int(os.getenv('QUEUE_MAX_RETRIES', 3))
HISTORY_RETENTION_DAYS: int = int(os.getenv('HISTORY_RETENTION_DAYS', 30))

# --- Режим разработки ---
DEBUG: bool = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

# --- Валидация URL для виджета ---
if WIDGET_BASE_URL == 'https://ваш-railway-url.railway.app':
    print("⚠️ WARNING: WIDGET_BASE_URL uses default value. Please update it in .env file!")

def get_config_dict() -> dict:
    """Возвращает словарь со всеми настройками для отладки"""
    return {
        'BOT_TOKEN': '***' if BOT_TOKEN else None,
        'DATABASE_URL': DATABASE_URL,
        'WEB_PORT': WEB_PORT,
        'WEB_HOST': WEB_HOST,
        'RATE_LIMIT': RATE_LIMIT,
        'CHECK_INTERVAL': CHECK_INTERVAL,
        'WARFRAME_API_URL': WARFRAME_API_URL,
        'WARFRAME_API_TIMEOUT': WARFRAME_API_TIMEOUT,
        'WIDGET_BASE_URL': WIDGET_BASE_URL,
        'LOG_LEVEL': LOG_LEVEL,
        'DEBUG': DEBUG,
        'HISTORY_RETENTION_DAYS': HISTORY_RETENTION_DAYS,
    }

def validate_config() -> bool:
    """Проверяет корректность конфигурации"""
    errors = []
    
    # Проверяем обязательные переменные
    if not BOT_TOKEN:
        errors.append("BOT_TOKEN is not set")
    
    # Проверяем числовые значения
    if WEB_PORT < 1 or WEB_PORT > 65535:
        errors.append(f"WEB_PORT must be between 1 and 65535, got {WEB_PORT}")
    
    if RATE_LIMIT < 1:
        errors.append(f"RATE_LIMIT must be at least 1, got {RATE_LIMIT}")
    
    if CHECK_INTERVAL < 10:
        errors.append(f"CHECK_INTERVAL must be at least 10 seconds, got {CHECK_INTERVAL}")
    
    if errors:
        for error in errors:
            print(f"❌ Config error: {error}")
        return False
    
    print("✅ Config validation passed")
    return True

# Автоматическая валидация при импорте
if __name__ != "__main__":
    if not validate_config():
        print("⚠️ Config validation failed. Check your .env file.")
