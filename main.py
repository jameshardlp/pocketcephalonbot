import asyncio
import threading
import os
import sys

from bot import WarframeBot
from web.server import run_web_server
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def run_worker():
    """Запуск бота"""
    try:
        bot = WarframeBot()
        asyncio.run(bot.start_bot())
    except Exception as e:
        logger.error(f"Worker error: {e}")

def run_web():
    """Запуск веб-сервера"""
    try:
        run_web_server()
    except Exception as e:
        logger.error(f"Web server error: {e}")

if __name__ == "__main__":
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1 and sys.argv[1] == "worker":
        run_worker()
    elif len(sys.argv) > 1 and sys.argv[1] == "web":
        run_web()
    else:
        # Запускаем оба процесса
        worker_thread = threading.Thread(target=run_worker, daemon=True)
        worker_thread.start()
        
        # Запускаем веб-сервер в основном потоке
        run_web()