import threading
import sys
import os

from bot import run_bot
from web.server import run_web_server
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start_worker():
    """Запуск воркера (бота)"""
    logger.info("Starting bot worker...")
    run_bot()

def start_web():
    """Запуск веб-сервера"""
    logger.info("Starting web server...")
    run_web_server()

if __name__ == "__main__":
    # Запускаем веб-сервер в основном потоке
    web_thread = threading.Thread(target=start_web, daemon=False)
    web_thread.start()
    
    # Запускаем бота в отдельном потоке
    worker_thread = threading.Thread(target=start_worker, daemon=True)
    worker_thread.start()
    
    # Ждем завершения
    try:
        web_thread.join()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)