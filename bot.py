import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import logging

from config import BOT_TOKEN
from handlers import start, help_command, settings, info_command, button_callback, widget_command
from scheduler import NotificationScheduler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class WarframeBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.scheduler = None
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков"""
        self.application.add_handler(CommandHandler("start", start))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("settings", settings))
        self.application.add_handler(CommandHandler("info", info_command))
        self.application.add_handler(CommandHandler("widget", widget_command))
        self.application.add_handler(CallbackQueryHandler(button_callback))
    
    async def start_bot(self):
        """Запуск бота"""
        try:
            # Инициализируем планировщик
            self.scheduler = NotificationScheduler(self.application.bot)
            self.scheduler.setup()
            
            # Запускаем бота
            logger.info("Starting bot...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            # Держим бота активным
            await asyncio.Event().wait()
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Остановка бота"""
        if self.scheduler:
            self.scheduler.scheduler.shutdown()
        await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()
        logger.info("Bot shut down")

def run_bot():
    """Запуск бота"""
    bot = WarframeBot()
    asyncio.run(bot.start_bot())

if __name__ == "__main__":
    run_bot()