from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import asyncio
import logging

from config import CHECK_INTERVAL
from database import add_to_queue, save_history
from warframe_api import WarframeAPI, format_notification

logger = logging.getLogger(__name__)

class NotificationScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.last_data = {}
        self.rate_limit = 5
        self.last_send_time = {}
        
    def setup(self):
        self.scheduler.add_job(
            self.check_all,
            trigger=IntervalTrigger(seconds=CHECK_INTERVAL),
            id='check_all',
            replace_existing=True
        )
        self.scheduler.start()
        logger.info("Scheduler started")
    
    async def check_all(self):
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
                self.check_nightwave()
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error in check_all: {e}")
    
    async def check_baro(self):
        data = await WarframeAPI.get_baro_trader()
        if data and data.get('active') and data.get('inventory'):
            key = 'baro_hash'
            baro_hash = hash(str(data.get('inventory', [])))
            if key not in self.last_data or self.last_data[key] != baro_hash:
                self.last_data[key] = baro_hash
                message = format_notification('baro', data)
                await self.notify_all('notify_baro', message, 'baro')
    
    async def check_fissures(self):
        data = await WarframeAPI.get_fissures()
        if data:
            key = 'fissures_hash'
            fissures_hash = hash(str([(f['id'], f['expiry']) for f in data]))
            if key not in self.last_data or self.last_data[key] != fissures_hash:
                self.last_data[key] = fissures_hash
                message = format_notification('fissures', data)
                await self.notify_all('notify_fissures', message, 'fissures')
    
    async def check_invasions(self):
        data = await WarframeAPI.get_invasions()
        if data:
            key = 'invasions_hash'
            invasions_hash = hash(str([(inv['id'], inv['completion']) for inv in data if inv.get('completion', 0) < 100]))
            if key not in self.last_data or self.last_data[key] != invasions_hash:
                self.last_data[key] = invasions_hash
                message = format_notification('invasions', data)
                await self.notify_all('notify_invasions', message, 'invasions')
    
    async def check_sortie(self):
        data = await WarframeAPI.get_sortie()
        if data:
            key = 'sortie_hash'
            sortie_hash = hash(str(data.get('variants', [])))
            if key not in self.last_data or self.last_data[key] != sortie_hash:
                self.last_data[key] = sortie_hash
                message = format_notification('sortie', data)
                await self.notify_all('notify_sortie', message, 'sortie')
    
    async def check_arbitration(self):
        data = await WarframeAPI.get_arbitration()
        if data:
            key = 'arbitration_hash'
            arb_hash = hash(str(data))
            if key not in self.last_data or self.last_data[key] != arb_hash:
                self.last_data[key] = arb_hash
                message = format_notification('arbitration', data)
                await self.notify_all('notify_arbitration', message, 'arbitration')
    
    async def check_archon(self):
        data = await WarframeAPI.get_archon_hunt()
        if data:
            key = 'archon_hash'
            archon_hash = hash(str(data.get('missions', [])))
            if key not in self.last_data or self.last_data[key] != archon_hash:
                self.last_data[key] = archon_hash
                message = format_notification('archon', data)
                await self.notify_all('notify_archon', message, 'archon')
    
    async def check_steel_path(self):
        data = await WarframeAPI.get_steel_path()
        if data and data.get('active'):
            key = 'steel_path_hash'
            sp_hash = hash(str(data.get('current_reward', {})))
            if key not in self.last_data or self.last_data[key] != sp_hash:
                self.last_data[key] = sp_hash
                message = format_notification('steel_path', data)
                await self.notify_all('notify_steel_path', message, 'steel_path')
    
    async def check_alerts(self):
        data = await WarframeAPI.get_alerts()
        if data:
            key = 'alerts_hash'
            alerts_hash = hash(str([(a['id'], a['expiry']) for a in data]))
            if key not in self.last_data or self.last_data[key] != alerts_hash:
                self.last_data[key] = alerts_hash
                message = format_notification('alerts', data)
                await self.notify_all('notify_alerts', message, 'alerts')
    
    async def check_cycles(self):
        earth = await WarframeAPI.get_earth_cycle()
        if earth:
            key = 'earth_hash'
            earth_hash = hash(str(earth.get('state')))
            if key not in self.last_data or self.last_data[key] != earth_hash:
                self.last_data[key] = earth_hash
                message = format_notification('earth_cycle', earth)
                await self.notify_all('notify_earth_cycle', message, 'earth_cycle')
        
        duviri = await WarframeAPI.get_duviri_mood()
        if duviri:
            key = 'duviri_hash'
            duviri_hash = hash(str(duviri.get('mood')))
            if key not in self.last_data or self.last_data[key] != duviri_hash:
                self.last_data[key] = duviri_hash
                message = format_notification('duviri_mood', duviri)
                await self.notify_all('notify_duviri_mood', message, 'duviri_mood')
    
    async def check_nightwave(self):
        data = await WarframeAPI.get_nightwave()
        if data:
            key = 'nightwave_hash'
            nightwave_hash = hash(str(data.get('offers', [])))
            if key not in self.last_data or self.last_data[key] != nightwave_hash:
                self.last_data[key] = nightwave_hash
                message = format_notification('nightwave', data)
                await self.notify_all('notify_nightwave', message, 'nightwave')
    
    async def notify_all(self, setting_name, message, notification_type):
        from database import Session, User
        session = Session()
        users = session.query(User).filter(getattr(User, setting_name) == True).all()
        session.close()
        
        for user in users:
            await self.send_notification(user.telegram_id, message, notification_type)
    
    async def send_notification(self, telegram_id, message, notification_type):
        now = datetime.utcnow()
        last_send = self.last_send_time.get(telegram_id)
        
        if last_send:
            time_diff = (now - last_send).total_seconds()
            if time_diff < self.rate_limit:
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
            add_to_queue(telegram_id, notification_type, message)
