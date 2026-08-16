from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import asyncio
import logging

from config import CHECK_INTERVAL
from database import get_pending_notifications, mark_as_sent, save_history, get_user, add_to_queue
from warframe_api import WarframeAPI, format_notification

logger = logging.getLogger(__name__)

class NotificationScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.last_data = {}
        self.rate_limit = 5  # секунд между сообщениями
        self.last_send_time = {}
        
    def setup(self):
        """Настройка планировщика"""
        # Основная проверка каждые 30 секунд
        self.scheduler.add_job(
            self.check_all,
            trigger=IntervalTrigger(seconds=CHECK_INTERVAL),
            id='check_all',
            replace_existing=True
        )
        
        # Проверка специальных событий каждую минуту
        self.scheduler.add_job(
            self.check_special_events,
            trigger=IntervalTrigger(seconds=60),
            id='check_special',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Scheduler started")
    
    async def check_all(self):
        """Проверка всех событий"""
        try:
            tasks = [
                self.check_baro(),
                self.check_fissures(),
                self.check_invasions(),
                self.check_sortie(),
                self.check_arbitration(),
                self.check_archon(),
                self.check_steel_path(),
                self.check_alerts(),
                self.check_cycles(),
                self.check_traders()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Обработка результатов
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Error in check: {result}")
                    
        except Exception as e:
            logger.error(f"Error in check_all: {e}")
    
    async def check_special_events(self):
        """Проверка специальных событий (реакторы, катализаторы)"""
        try:
            invasions = await WarframeAPI.get_invasions()
            if invasions:
                for invasion in invasions:
                    reward = invasion.get('reward', {})
                    reward_name = reward.get('itemName', '')
                    
                    if 'реактор' in reward_name.lower() or 'reactor' in reward_name.lower():
                        await self.notify_special_reward('reactor', invasion)
                    elif 'катализатор' in reward_name.lower() or 'catalyst' in reward_name.lower():
                        await self.notify_special_reward('catalyst', invasion)
                        
        except Exception as e:
            logger.error(f"Error in check_special_events: {e}")
    
    async def notify_special_reward(self, reward_type, data):
        """Уведомление о специальных наградах"""
        message = format_notification('special_reward', {
            'type': reward_type,
            'node': data.get('node', ''),
            'expiry': data.get('expiry', '')
        })
        
        # Отправляем всем пользователям, у которых включены уведомления
        from database import Session, User
        session = Session()
        users = session.query(User).filter(
            User.notify_reactor == True if reward_type == 'reactor' else User.notify_catalyst == True
        ).all()
        session.close()
        
        for user in users:
            await self.send_notification(user.telegram_id, message, f'special_{reward_type}')
    
    async def check_baro(self):
        """Проверка торговца из Бездны"""
        data = await WarframeAPI.get_baro_trader()
        if data and data.get('active'):
            # Проверяем, изменился ли инвентарь
            key = 'baro_inventory'
            inventory_hash = hash(str(data.get('inventory', [])))
            
            if key not in self.last_data or self.last_data[key] != inventory_hash:
                self.last_data[key] = inventory_hash
                message = format_notification('baro', data)
                await self.notify_all('notify_baro', message, 'baro')
    
    async def check_fissures(self):
        """Проверка разрывов Бездны"""
        data = await WarframeAPI.get_fissures()
        if data:
            # Проверяем, изменился ли список
            key = 'fissures_list'
            fissures_hash = hash(str([(f['id'], f['expiry']) for f in data]))
            
            if key not in self.last_data or self.last_data[key] != fissures_hash:
                self.last_data[key] = fissures_hash
                message = format_notification('fissures', data)
                await self.notify_all('notify_fissures', message, 'fissures')
    
    async def check_invasions(self):
        """Проверка вторжений"""
        data = await WarframeAPI.get_invasions()
        if data:
            key = 'invasions_list'
            invasions_hash = hash(str([(inv['id'], inv['completion']) for inv in data]))
            
            if key not in self.last_data or self.last_data[key] != invasions_hash:
                self.last_data[key] = invasions_hash
                message = format_notification('invasions', data)
                await self.notify_all('notify_invasions', message, 'invasions')
    
    async def check_sortie(self):
        """Проверка сортировки"""
        data = await WarframeAPI.get_sortie()
        if data:
            key = 'sortie_data'
            sortie_hash = hash(str(data.get('variants', [])))
            
            if key not in self.last_data or self.last_data[key] != sortie_hash:
                self.last_data[key] = sortie_hash
                message = format_notification('sortie', data)
                await self.notify_all('notify_sortie', message, 'sortie')
    
    async def check_arbitration(self):
        """Проверка арбитража"""
        data = await WarframeAPI.get_arbitration()
        if data:
            key = 'arbitration_data'
            arb_hash = hash(str(data))
            
            if key not in self.last_data or self.last_data[key] != arb_hash:
                self.last_data[key] = arb_hash
                message = format_notification('arbitration', data)
                await self.notify_all('notify_arbitration', message, 'arbitration')
    
    async def check_archon(self):
        """Проверка охоты на Архонтов"""
        data = await WarframeAPI.get_archon_hunt()
        if data:
            key = 'archon_data'
            archon_hash = hash(str(data.get('missions', [])))
            
            if key not in self.last_data or self.last_data[key] != archon_hash:
                self.last_data[key] = archon_hash
                message = format_notification('archon', data)
                await self.notify_all('notify_archon', message, 'archon')
    
    async def check_steel_path(self):
        """Проверка Стального Пути"""
        data = await WarframeAPI.get_steel_path()
        if data and data.get('active'):
            key = 'steel_path_data'
            sp_hash = hash(str(data.get('current_reward', {})))
            
            if key not in self.last_data or self.last_data[key] != sp_hash:
                self.last_data[key] = sp_hash
                message = format_notification('steel_path', data)
                await self.notify_all('notify_steel_path', message, 'steel_path')
    
    async def check_alerts(self):
        """Проверка тревог"""
        data = await WarframeAPI.get_alerts()
        if data:
            key = 'alerts_list'
            alerts_hash = hash(str([(alert['id'], alert['expiry']) for alert in data]))
            
            if key not in self.last_data or self.last_data[key] != alerts_hash:
                self.last_data[key] = alerts_hash
                message = format_notification('alerts', data)
                await self.notify_all('notify_alerts', message, 'alerts')
    
    async def check_cycles(self):
        """Проверка циклов и погоды"""
        # Земля
        earth = await WarframeAPI.get_earth_cycle()
        if earth:
            key = 'earth_cycle'
            earth_hash = hash(str(earth.get('state')))
            if key not in self.last_data or self.last_data[key] != earth_hash:
                self.last_data[key] = earth_hash
                message = format_notification('earth_cycle', earth)
                await self.notify_all('notify_earth_cycle', message, 'earth_cycle')
        
        # Венера
        venus = await WarframeAPI.get_venus_weather()
        if venus:
            key = 'venus_weather'
            venus_hash = hash(str(venus.get('state')))
            if key not in self.last_data or self.last_data[key] != venus_hash:
                self.last_data[key] = venus_hash
                message = format_notification('venus_weather', venus)
                await self.notify_all('notify_venus_weather', message, 'venus_weather')
        
        # Деймос
        deimos = await WarframeAPI.get_deimos_cycle()
        if deimos:
            key = 'deimos_cycle'
            deimos_hash = hash(str(deimos.get('state')))
            if key not in self.last_data or self.last_data[key] != deimos_hash:
                self.last_data[key] = deimos_hash
                message = format_notification('deimos_cycle', deimos)
                await self.notify_all('notify_deimos_cycle', message, 'deimos_cycle')
        
        # Дувири
        duviri = await WarframeAPI.get_duviri_mood()
        if duviri:
            key = 'duviri_mood'
            duviri_hash = hash(str(duviri.get('mood')))
            if key not in self.last_data or self.last_data[key] != duviri_hash:
                self.last_data[key] = duviri_hash
                message = format_notification('duviri_mood', duviri)
                await self.notify_all('notify_duviri_mood', message, 'duviri_mood')
    
    async def check_traders(self):
        """Проверка торговцев"""
        # Эрго Гласт
        ergo = await WarframeAPI.get_ergo_glast()
        if ergo and ergo.get('inventory'):
            key = 'ergo_glast'
            ergo_hash = hash(str(ergo.get('inventory', [])))
            if key not in self.last_data or self.last_data[key] != ergo_hash:
                self.last_data[key] = ergo_hash
                message = format_notification('ergo_glast', ergo)
                await self.notify_all('notify_ergo_glast', message, 'ergo_glast')
        
        # Элеонора
        eleonora = await WarframeAPI.get_eleonora()
        if eleonora and eleonora.get('inventory'):
            key = 'eleonora'
            eleonora_hash = hash(str(eleonora.get('inventory', [])))
            if key not in self.last_data or self.last_data[key] != eleonora_hash:
                self.last_data[key] = eleonora_hash
                message = format_notification('eleonora', eleonora)
                await self.notify_all('notify_eleonora', message, 'eleonora')
    
    async def notify_all(self, setting_name, message, notification_type):
        """Отправка уведомлений всем пользователям с включенным типом"""
        from database import Session, User
        session = Session()
        users = session.query(User).filter(getattr(User, setting_name) == True).all()
        session.close()
        
        for user in users:
            await self.send_notification(user.telegram_id, message, notification_type)
    
    async def send_notification(self, telegram_id, message, notification_type):
        """Отправка уведомления с учетом rate limit"""
        now = datetime.utcnow()
        last_send = self.last_send_time.get(telegram_id)
        
        if last_send:
            time_diff = (now - last_send).total_seconds()
            if time_diff < self.rate_limit:
                # Добавляем в очередь
                add_to_queue(telegram_id, notification_type, message)
                return
        
        try:
            await self.bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode='Markdown'
            )
            self.last_send_time[telegram_id] = now
            save_history(telegram_id, notification_type, message)
        except Exception as e:
            logger.error(f"Error sending notification to {telegram_id}: {e}")
            # Добавляем в очередь для повторной отправки
            add_to_queue(telegram_id, notification_type, message)
    
    async def process_queue(self):
        """Обработка очереди уведомлений"""
        notifications = get_pending_notifications()
        
        for notification in notifications:
            await self.send_notification(
                notification.user_id,
                notification.content,
                notification.notification_type
            )
            mark_as_sent(notification.id)