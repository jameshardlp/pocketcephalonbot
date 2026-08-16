#!/usr/bin/env python3
import asyncio
import threading
import sys
import os
import time
import logging
import signal

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot import run_bot
from web.server import run_web_server

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start_bot():
    """Запуск бота с повторными попытками"""
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            logger.info(f"🚀 Starting bot (attempt {attempt + 1}/{max_retries})...")
            run_bot()
            break
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")
            if attempt < max_retries - 1:
                logger.info(f"⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("❌ Bot failed to start after all retries")
                raise

def start_web():
    """Запуск веб-сервера"""
    try:
        logger.info("🌐 Starting web server...")
        run_web_server()
    except Exception as e:
        logger.error(f"❌ Web server error: {e}")
        raise

def signal_handler(signum, frame):
    """Обработка сигналов для graceful shutdown"""
    logger.info(f"📡 Received signal {signum}, shutting down...")
    sys.exit(0)

if __name__ == "__main__":
    # Настройка обработчиков сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("📦 Starting Warframe Bot...")
    logger.info(f"🐍 Python version: {sys.version}")
    logger.info(f"📂 Working directory: {os.getcwd()}")
    
    # Проверяем наличие токена
    if not os.getenv('BOT_TOKEN'):
        logger.error("❌ BOT_TOKEN not set! Please set it in environment variables.")
        sys.exit(1)
    
    # Запускаем веб-сервер в основном потоке
    web_thread = threading.Thread(target=start_web, daemon=False)
    web_thread.start()
    
    # Даем веб-серверу время на запуск
    time.sleep(2)
    
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Ждем завершения
    try:
        web_thread.join()
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
        sys.exit(0)
