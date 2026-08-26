from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import asyncio
import logging
import random

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
        self.user_cache = {}  # Кеш пользователей для уменьшения нагрузки на БД
        self.cache_time = {}
        self.cache_ttl = 60  # Обновлять кеш каждые 60 секунд
        
    def setup(self):
        # Добавляем небольшую случайную задержку при старте
        initial_delay = random.randint(5, 15)
        
        self.scheduler.add_job(
            self.check_all,
            trigger=IntervalTrigger(seconds=CHECK_INTERVAL),
            id='check_all',
            replace_existing=True,
            misfire_grace_time=30
        )
        self.scheduler.start()
        logger.info(f"Scheduler started (initial delay: {initial_delay}s, interval: {CHECK_INTERVAL}s)")
    
    async def check_all(self):
        """Основная проверка всех событий"""
        try:
            logger.debug("Starting check_all cycle")
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
            
            # Добавляем таймаут для всех задач
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Логируем ошибки отдельных задач
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Task {i} failed: {result}")
                    
        except Exception as e:
            logger.error(f"Error in check_all: {e}")
    
    async def get_users_with_setting(self, setting_name):
        """Получение пользователей с включенным уведомлением (с кешированием)"""
        from database import Session, User
        
        cache_key = setting_name
        current_time = datetime.utcnow().timestamp()
        
        # Проверяем кеш
        if cache_key in self.user_cache and cache_key in self.cache_time:
            if current_time - self.cache_time[cache_key] < self.cache_ttl:
                return self.user_cache[cache_key]
        
        # Получаем из БД
        session = Session()
        try:
            users = session.query(User).filter(getattr(User, setting_name) == True).all()
            user_ids = [user.telegram_id for user in users]
            
            # Обновляем кеш
            self.user_cache[cache_key] = user_ids
            self.cache_time[cache_key] = current_time
            
            return user_ids
        except Exception as e:
            logger.error(f"Error getting users for {setting_name}: {e}")
            return []
        finally:
            session.close()
    
    async def check_baro(self):
        try:
            data = await WarframeAPI.get_baro_trader()
            if data and data.get('active') and data.get('inventory'):
                key = 'baro_hash'
                baro_hash = hash(str(sorted(
                    [(item.get('item', ''), item.get('ducats', 0), item.get('credits', 0)) 
                     for item in data.get('inventory', [])]
                )))
                if key not in self.last_data or self.last_data[key] != baro_hash:
                    self.last_data[key] = baro_hash
                    message = format_notification('baro', data)
                    if message:
                        await self.notify_all('notify_baro', message, 'baro')
        except Exception as e:
            logger.error(f"Error in check_baro: {e}")
    
    async def check_fissures(self):
        try:
            data = await WarframeAPI.get_fissures()
            if data:
                key = 'fissures_hash'
                fissures_hash = hash(str(sorted([(f['id'], f['expiry']) for f in data])))
                if key not in self.last_data or self.last_data[key] != fissures_hash:
                    self.last_data[key] = fissures_hash
                    message = format_notification('fissures', data)
                    if message:
                        await self.notify_all('notify_fissures', message, 'fissures')
        except Exception as e:
            logger.error(f"Error in check_fissures: {e}")
    
    async def check_invasions(self):
        try:
            data = await WarframeAPI.get_invasions()
            if data:
                key = 'invasions_hash'
                active_invasions = [inv for inv in data if inv.get('completion', 0) < 100]
                if active_invasions:
                    invasions_hash = hash(str(sorted([
                        (inv['id'], inv['completion']) 
                        for inv in active_invasions
                    ])))
                    if key not in self.last_data or self.last_data[key] != invasions_hash:
                        self.last_data[key] = invasions_hash
                        message = format_notification('invasions', data)
                        if message:
                            await self.notify_all('notify_invasions', message, 'invasions')
        except Exception as e:
            logger.error(f"Error in check_invasions: {e}")
    
    async def check_sortie(self):
        try:
            data = await WarframeAPI.get_sortie()
            if data:
                key = 'sortie_hash'
                sortie_hash = hash(str(sorted([
                    (v.get('node', ''), v.get('mission_type', '')) 
                    for v in data.get('variants', [])
                ])))
                if key not in self.last_data or self.last_data[key] != sortie_hash:
                    self.last_data[key] = sortie_hash
                    message = format_notification('sortie', data)
                    if message:
                        await self.notify_all('notify_sortie', message, 'sortie')
        except Exception as e:
            logger.error(f"Error in check_sortie: {e}")
    
    async def check_arbitration(self):
        try:
            data = await WarframeAPI.get_arbitration()
            if data:
                key = 'arbitration_hash'
                arb_hash = hash(str({
                    'node': data.get('node', ''),
                    'type': data.get('type', ''),
                    'enemy': data.get('enemy', ''),
                    'source': data.get('source', '')
                }))
                if key not in self.last_data or self.last_data[key] != arb_hash:
                    self.last_data[key] = arb_hash
                    message = format_notification('arbitration', data)
                    if message:
                        await self.notify_all('notify_arbitration', message, 'arbitration')
        except Exception as e:
            logger.error(f"Error in check_arbitration: {e}")
    
    async def check_archon(self):
        try:
            data = await WarframeAPI.get_archon_hunt()
            if data:
                key = 'archon_hash'
                archon_hash = hash(str(sorted([
                    (m.get('node', ''), m.get('type', '')) 
                    for m in data.get('missions', [])
                ])))
                if key not in self.last_data or self.last_data[key] != archon_hash:
                    self.last_data[key] = archon_hash
                    message = format_notification('archon', data)
                    if message:
                        await self.notify_all('notify_archon', message, 'archon')
        except Exception as e:
            logger.error(f"Error in check_archon: {e}")
    
    async def check_steel_path(self):
        try:
            data = await WarframeAPI.get_steel_path()
            if data and data.get('active'):
                key = 'steel_path_hash'
                reward = data.get('current_reward', {})
                sp_hash = hash(str({
                    'reward_name': reward.get('name', ''),
                    'remaining': data.get('remaining', '')
                }))
                if key not in self.last_data or self.last_data[key] != sp_hash:
                    self.last_data[key] = sp_hash
                    message = format_notification('steel_path', data)
                    if message:
                        await self.notify_all('notify_steel_path', message, 'steel_path')
        except Exception as e:
            logger.error(f"Error in check_steel_path: {e}")
    
    async def check_alerts(self):
        try:
            data = await WarframeAPI.get_alerts()
            if data:
                key = 'alerts_hash'
                alerts_hash = hash(str(sorted([(a['id'], a['expiry']) for a in data])))
                if key not in self.last_data or self.last_data[key] != alerts_hash:
                    self.last_data[key] = alerts_hash
                    message = format_notification('alerts', data)
                    if message:
                        await self.notify_all('notify_alerts', message, 'alerts')
        except Exception as e:
            logger.error(f"Error in check_alerts: {e}")
    
    async def check_cycles(self):
        # Земля
        try:
            earth = await WarframeAPI.get_earth_cycle()
            if earth:
                key = 'earth_hash'
                earth_hash = hash(str(earth.get('state')))
                if key not in self.last_data or self.last_data[key] != earth_hash:
                    self.last_data[key] = earth_hash
                    message = format_notification('earth_cycle', earth)
                    if message:
                        await self.notify_all('notify_earth_cycle', message, 'earth_cycle')
        except Exception as e:
            logger.error(f"Error in check_earth_cycle: {e}")
        
        # Венера
        try:
            venus = await WarframeAPI.get_venus_weather()
            if venus:
                key = 'venus_hash'
                venus_hash = hash(str(venus.get('state')))
                if key not in self.last_data or self.last_data[key] != venus_hash:
                    self.last_data[key] = venus_hash
                    message = format_notification('venus_weather', venus)
                    if message:
                        await self.notify_all('notify_venus_weather', message, 'venus_weather')
        except Exception as e:
            logger.error(f"Error in check_venus_weather: {e}")
        
        # Деймос
        try:
            deimos = await WarframeAPI.get_deimos_cycle()
            if deimos:
                key = 'deimos_hash'
                deimos_hash = hash(str(deimos.get('state')))
                if key not in self.last_data or self.last_data[key] != deimos_hash:
                    self.last_data[key] = deimos_hash
                    message = format_notification('deimos_cycle', deimos)
                    if message:
                        await self.notify_all('notify_deimos_cycle', message, 'deimos_cycle')
        except Exception as e:
            logger.error(f"Error in check_deimos_cycle: {e}")
        
        # Дувири
        try:
            duviri = await WarframeAPI.get_duviri_mood()
            if duviri:
                key = 'duviri_hash'
                duviri_hash = hash(str(duviri.get('mood')))
                if key not in self.last_data or self.last_data[key] != duviri_hash:
                    self.last_data[key] = duviri_hash
                    message = format_notification('duviri_mood', duviri)
                    if message:
                        await self.notify_all('notify_duviri_mood', message, 'duviri_mood')
        except Exception as e:
            logger.error(f"Error in check_duviri_mood: {e}")
    
    async def check_nightwave(self):
        try:
            data = await WarframeAPI.get_nightwave()
            if data:
                key = 'nightwave_hash'
                nightwave_hash = hash(str(sorted([
                    (o.get('name', ''), o.get('cost', {}).get('nightwave_credits', 0))
                    for o in data.get('offers', [])
                ])))
                if key not in self.last_data or self.last_data[key] != nightwave_hash:
                    self.last_data[key] = nightwave_hash
                    message = format_notification('nightwave', data)
                    if message:
                        await self.notify_all('notify_nightwave', message, 'nightwave')
        except Exception as e:
            logger.error(f"Error in check_nightwave: {e}")
    
    async def notify_all(self, setting_name, message, notification_type):
        """Отправка уведомлений всем пользователям с включенным типом"""
        try:
            user_ids = await self.get_users_with_setting(setting_name)
            
            if not user_ids:
                logger.debug(f"No users for {setting_name}")
                return
            
            logger.info(f"Sending {notification_type} to {len(user_ids)} users")
            
            # Отправляем с ограничением скорости
            for i, user_id in enumerate(user_ids):
                # Добавляем небольшую задержку между пользователями
                if i > 0:
                    await asyncio.sleep(0.1)
                
                await self.send_notification(user_id, message, notification_type)
                
        except Exception as e:
            logger.error(f"Error in notify_all for {setting_name}: {e}")
    
    async def send_notification(self, telegram_id, message, notification_type):
        """Отправка одного уведомления с rate limiting"""
        now = datetime.utcnow()
        last_send = self.last_send_time.get(telegram_id)
        
        # Проверяем rate limit
        if last_send:
            time_diff = (now - last_send).total_seconds()
            if time_diff < self.rate_limit:
                # Ставим в очередь
                add_to_queue(telegram_id, notification_type, message)
                logger.debug(f"Rate limited {telegram_id}, queued {notification_type}")
                return
        
        try:
            await self.bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode='Markdown'
            )
            self.last_send_time[telegram_id] = now
            save_history(telegram_id, notification_type, message)
            logger.info(f"Sent {notification_type} to {telegram_id}")
            
        except Exception as e:
            logger.error(f"Error sending to {telegram_id}: {e}")
            # При ошибке добавляем в очередь для повторной попытки
            add_to_queue(telegram_id, notification_type, message)
