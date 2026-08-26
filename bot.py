import asyncio
import logging
import os
import sys
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from config import BOT_TOKEN
from handlers import start, help_command, settings, info_command, button_callback, widget_command
from scheduler import NotificationScheduler
from database import init_db

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class WarframeBot:
    def __init__(self):
        self.token = BOT_TOKEN
        if not self.token:
            raise ValueError("BOT_TOKEN is not set!")
        
        logger.info("🤖 Initializing Warframe Bot...")
        self.application = Application.builder().token(self.token).build()
        self.scheduler = None
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков"""
        logger.info("📝 Setting up handlers...")
        self.application.add_handler(CommandHandler("start", start))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("settings", settings))
        self.application.add_handler(CommandHandler("info", info_command))
        self.application.add_handler(CommandHandler("widget", widget_command))
        self.application.add_handler(CallbackQueryHandler(button_callback))
        logger.info("✅ Handlers set up")
    
    async def start_bot(self):
        """Запуск бота"""
        try:
            logger.info("🚀 Initializing bot application...")
            
            # Инициализируем базу данных
            init_db()
            
            # Инициализируем планировщик
            logger.info("⏰ Setting up scheduler...")
            self.scheduler = NotificationScheduler(self.application.bot)
            self.scheduler.setup()
            
            # Запускаем бота
            logger.info("🔄 Starting bot polling...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("✅ Bot is running!")
            
            # Держим бота активным
            while True:
                await asyncio.sleep(3600)
                logger.debug("💓 Bot heartbeat")
            
        except asyncio.CancelledError:
            logger.info("🔄 Bot task cancelled")
        except Exception as e:
            logger.error(f"❌ Error starting bot: {e}", exc_info=True)
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Остановка бота"""
        logger.info("🛑 Shutting down bot...")
        if self.scheduler:
            try:
                self.scheduler.scheduler.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down scheduler: {e}")
        try:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        logger.info("✅ Bot shut down")

def run_bot():
    """Запуск бота"""
    try:
        bot = WarframeBot()
        asyncio.run(bot.start_bot())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    run_bot()
