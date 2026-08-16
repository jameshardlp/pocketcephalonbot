import aiohttp
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import re

WARFRAME_API_URL = "https://api.warframestat.us/pc"

class WarframeAPI:
    @staticmethod
    async def fetch_data(endpoint: str) -> Optional[Dict]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{WARFRAME_API_URL}/{endpoint}") as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception as e:
            print(f"Error fetching {endpoint}: {e}")
            return None
    
    @staticmethod
    async def get_baro_trader() -> Optional[Dict]:
        data = await WarframeAPI.fetch_data("voidTrader")
        if data:
            return {
                'active': data.get('active', False),
                'location': data.get('location', 'Неизвестно'),
                'inventory': data.get('inventory', []),
                'end': data.get('end', ''),
                'start': data.get('start', ''),
                'character': data.get('character', "Baro Ki'Teer")
            }
        return None
    
    @staticmethod
    async def get_fissures() -> Optional[List[Dict]]:
        data = await WarframeAPI.fetch_data("fissures")
        if data:
            return [{
                'id': fissure.get('id', ''),
                'tier': fissure.get('tier', ''),
                'node': fissure.get('node', ''),
                'mission_type': fissure.get('missionType', ''),
                'enemy': fissure.get('enemy', ''),
                'expiry': fissure.get('expiry', ''),
                'active': fissure.get('active', False),
                'tier_num': fissure.get('tierNum', 0),
                'is_storm': fissure.get('isStorm', False),
                'eta': fissure.get('eta', '')
            } for fissure in data if fissure.get('active', False)]
        return []
    
    @staticmethod
    async def get_invasions() -> Optional[List[Dict]]:
        data = await WarframeAPI.fetch_data("invasions")
        if data:
            return [{
                'id': invasion.get('id', ''),
                'node': invasion.get('node', ''),
                'faction': invasion.get('faction', ''),
                'attacker': invasion.get('attacker', {}),
                'defender': invasion.get('defender', {}),
                'completion': invasion.get('completion', 0),
                'reward': invasion.get('reward', {}),
                'eta': invasion.get('eta', ''),
                'vs': invasion.get('vs', ''),
                'description': invasion.get('desc', '')
            } for invasion in data]
        return []
    
    @staticmethod
    async def get_sortie() -> Optional[Dict]:
        data = await WarframeAPI.fetch_data("sortie")
        if data:
            return {
                'boss': data.get('boss', ''),
                'faction': data.get('faction', ''),
                'variants': data.get('variants', []),
                'expiry': data.get('expiry', ''),
                'reward_pool': data.get('rewardPool', [])
            }
        return None
    
    @staticmethod
    async def get_arbitration() -> Optional[Dict]:
        data = await WarframeAPI.fetch_data("arbitration")
        if data:
            return {
                'node': data.get('node', ''),
                'type': data.get('type', ''),
                'enemy': data.get('enemy', ''),
                'expiry': data.get('expiry', ''),
                'node_key': data.get('nodeKey', ''),
                'tier': data.get('tier', ''),
                'mission_type': data.get('missionType', ''),
                'archwing': data.get('archwing', False),
                'dark_sector': data.get('darkSector', False)
            }
        return None
    
    @staticmethod
    async def get_archon_hunt() -> Optional[Dict]:
        data = await WarframeAPI.fetch_data("archonHunt")
        if data:
            return {
                'boss': data.get('boss', ''),
                'faction': data.get('faction', ''),
                'missions': data.get('missions', []),
                'expiry': data.get('expiry', ''),
                'reward_pool': data.get('rewardPool', [])
            }
        return None
    
    @staticmethod
    async def get_steel_path() -> Optional[Dict]:
        data = await WarframeAPI.fetch_data("steelPath")
        if data:
            return {
                'active': data.get('active', False),
                'current_reward': data.get('currentReward', {}),
                'rotation': data.get('rotation', ''),
                'expiry': data.get('expiry', ''),
                'remaining': data.get('remaining', '')
            }
        return None
    
    @staticmethod
    async def get_alerts() -> Optional[List[Dict]]:
        data = await WarframeAPI.fetch_data("alerts")
        if data:
            return [{
                'id': alert.get('id', ''),
                'mission': alert.get('mission', {}),
                'reward': alert.get('reward', {}),
                'expiry': alert.get('expiry', ''),
                'eta': alert.get('eta', '')
            } for alert in data]
        return []
    
    @staticmethod
    async def get_earth_cycle() -> Optional[Dict]:
        data = await WarframeAPI.fetch_data("earthCycle")
        if data:
            return {
                'state': data.get('state', ''),
                'time_left': data.get('timeLeft', ''),
                'is_day': data.get('isDay', False)
            }
        return None
    
    @staticmethod
    async def get_venus_weather() -> Optional[Dict]:
        data = await WarframeAPI.fetch_data("venusWeather")
        if data:
            return {
                'state': data.get('state', ''),
                'time_left': data.get('timeLeft', ''),
                'is_warm': data.get('isWarm', False)
            }
        return None
    
    @staticmethod
    async def get_deimos_cycle() -> Optional[Dict]:
        data = await WarframeAPI.fetch_data("deimosCycle")
        if data:
            return {
                'state': data.get('state', ''),
                'time_left': data.get('timeLeft', ''),
                'is_vome': data.get('isVome', False)
            }
        return None
    
    @staticmethod
    async def get_duviri_mood() -> Optional[Dict]:
        data = await WarframeAPI.fetch_data("duviriCycle")
        if data:
            return {
                'mood': data.get('mood', ''),
                'time_left': data.get('timeLeft', ''),
                'mood_icon': data.get('moodIcon', '')
            }
        return None
    
    @staticmethod
    async def get_ergo_glast() -> Optional[Dict]:
        data = await WarframeAPI.fetch_data("ergoGlast")
        if data:
            return {
                'inventory': data.get('inventory', []),
                'expiry': data.get('expiry', '')
            }
        return None
    
    @staticmethod
    async def get_eleonora() -> Optional[Dict]:
        data = await WarframeAPI.fetch_data("eleonora")
        if data:
            return {
                'inventory': data.get('inventory', []),
                'expiry': data.get('expiry', '')
            }
        return None

def parse_weapon_stats(item_data: Dict) -> str:
    """Парсинг характеристик оружия"""
    stats = []
    if 'stats' in item_data:
        for stat in item_data['stats']:
            if stat.get('positive', ''):
                stats.append(f"✅ {stat['positive']}")
            if stat.get('negative', ''):
                stats.append(f"❌ {stat['negative']}")
    return "\n".join(stats) if stats else "Нет данных"

def format_notification(data_type: str, data) -> str:
    """Форматирование уведомлений"""
    
    if data_type == 'baro':
        if not data or not data.get('active'):
            return "🚫 Торговец из Бездны сейчас неактивен"
        
        # Исправлено: используем двойные кавычки для строки с апострофом
        character_name = data.get('character', "Baro Ki'Teer")
        message = f"🧛 **{character_name}**\n"
        message += f"📍 **Местоположение:** {data['location']}\n"
        message += f"⏰ **Доступен до:** {data['end']}\n\n"
        message += "**🛍️ Инвентарь:**\n"
        
        for item in data.get('inventory', [])[:10]:
            item_name = item.get('item', 'Неизвестно')
            cost = item.get('cost', {})
            ducats = cost.get('ducats', 0)
            credits = cost.get('credits', 0)
            message += f"• {item_name} - {ducats}🪙 {credits}💰\n"
        
        return message
    
    elif data_type == 'fissures':
        if not data:
            return "🚫 Активных разрывов Бездны нет"
        
        message = "💠 **Активные разрывы Бездны**\n\n"
        tier_order = {'Лито': 1, 'Мезо': 2, 'Нео': 3, 'Акси': 4}
        
        sorted_fissures = sorted(data, key=lambda x: tier_order.get(x['tier'], 99))
        
        for fissure in sorted_fissures[:15]:
            storm = "⚡ " if fissure.get('is_storm') else ""
            message += f"{storm}**{fissure['tier']}** - {fissure['node']}\n"
            message += f"  {fissure['mission_type']} vs {fissure['enemy']}\n"
            if fissure.get('eta'):
                message += f"  ⏰ {fissure['eta']}\n"
            message += "\n"
        
        return message
    
    elif data_type == 'invasions':
        if not data:
            return "🚫 Активных вторжений нет"
        
        message = "⚔️ **Активные вторжения**\n\n"
        
        for invasion in data[:10]:
            attacker = invasion.get('attacker', {})
            defender = invasion.get('defender', {})
            reward = invasion.get('reward', {})
            
            message += f"📍 **{invasion['node']}**\n"
            message += f"⚔️ {attacker.get('name', 'Неизвестно')} vs {defender.get('name', 'Неизвестно')}\n"
            message += f"📊 Прогресс: {invasion.get('completion', 0):.1f}%\n"
            
            if reward:
                reward_type = reward.get('type', '')
                reward_name = reward.get('itemName', '')
                if reward_type == 'reactor' or 'реактор' in reward_name.lower():
                    message += "⚡ **Награда: Реактор Орокин!**\n"
                elif reward_type == 'catalyst' or 'катализатор' in reward_name.lower():
                    message += "🔧 **Награда: Катализатор Орокин!**\n"
                else:
                    message += f"🎁 Награда: {reward_name}\n"
            
            if invasion.get('eta'):
                message += f"⏰ {invasion['eta']}\n"
            message += "\n"
        
        return message
    
    elif data_type == 'sortie':
        if not data:
            return "🚫 Сортировка сейчас недоступна"
        
        message = "🎯 **Сортировка**\n\n"
        message += f"👾 Босс: {data['boss']}\n"
        message += f"⚔️ Фракция: {data['faction']}\n"
        message += f"⏰ Доступна до: {data['expiry']}\n\n"
        message += "**📋 Задания:**\n"
        
        for variant in data.get('variants', []):
            message += f"• {variant.get('node', '')} - {variant.get('modifier', '')}\n"
            message += f"  {variant.get('missionType', '')}\n"
        
        if data.get('reward_pool'):
            message += f"\n**🎁 Награды:**\n"
            for reward in data['reward_pool'][:3]:
                message += f"• {reward}\n"
        
        return message
    
    elif data_type == 'arbitration':
        if not data:
            return "🚫 Арбитраж сейчас недоступен"
        
        message = "⚡ **Арбитраж**\n\n"
        message += f"📍 **Узел:** {data['node']}\n"
        message += f"🎯 **Тип миссии:** {data['mission_type']}\n"
        message += f"👾 **Враг:** {data['enemy']}\n"
        message += f"⭐ **Тир карты:** {data.get('tier', 'Обычный')}\n"
        message += f"⏰ **Доступен до:** {data['expiry']}\n"
        
        if data.get('archwing'):
            message += "🛸 **Арчвинг активен**\n"
        if data.get('dark_sector'):
            message += "🌑 **Темный сектор**\n"
        
        # Добавляем рекомендации
        recommendations = []
        if 'выживание' in data['mission_type'].lower():
            recommendations.append("💡 Рекомендуется: Танк/Поддержка")
        elif 'захват' in data['mission_type'].lower():
            recommendations.append("💡 Рекомендуется: Быстрый фрейм")
        elif 'оборона' in data['mission_type'].lower():
            recommendations.append("💡 Рекомендуется: Контроль толпы")
        
        if recommendations:
            message += "\n" + "\n".join(recommendations)
        
        return message
    
    elif data_type == 'archon':
        if not data:
            return "🚫 Охота на Архонтов сейчас недоступна"
        
        message = "🔥 **Охота на Архонтов**\n\n"
        message += f"👾 Босс: {data['boss']}\n"
        message += f"⚔️ Фракция: {data['faction']}\n"
        message += f"⏰ Доступна до: {data['expiry']}\n\n"
        message += "**📋 Миссии:**\n"
        
        for mission in data.get('missions', []):
            message += f"• {mission.get('node', '')} - {mission.get('type', '')}\n"
            message += f"  {mission.get('modifier', '')}\n"
        
        return message
    
    elif data_type == 'steel_path':
        if not data or not data.get('active'):
            return "🚫 Стальной Путь сейчас неактивен"
        
        message = "🗡️ **Стальной Путь**\n\n"
        reward = data.get('current_reward', {})
        if reward:
            message += f"🎁 **Текущая награда:** {reward.get('name', 'Неизвестно')}\n"
            message += f"🔄 **Ротация:** {data.get('rotation', '')}\n"
            message += f"⏰ **Доступно:** {data.get('remaining', '')}\n"
            message += f"📊 **Информация:** {reward.get('description', '')}\n"
        else:
            message += "Текущая награда не определена\n"
        
        return message
    
    elif data_type == 'alerts':
        if not data:
            return "🚫 Активных тревог нет"
        
        message = "🚨 **Активные тревоги**\n\n"
        
        for alert in data[:10]:
            mission = alert.get('mission', {})
            reward = alert.get('reward', {})
            
            message += f"📍 **{mission.get('node', '')}**\n"
            message += f"🎯 {mission.get('type', '')} - {mission.get('faction', '')}\n"
            
            if reward:
                reward_name = reward.get('asString', '')
                reward_credits = reward.get('credits', 0)
                message += f"🎁 Награда: {reward_name} ({reward_credits}💰)\n"
            
            if alert.get('eta'):
                message += f"⏰ {alert['eta']}\n"
            message += "\n"
        
        return message
    
    elif data_type == 'earth_cycle':
        if not data:
            return "🌍 Данные о цикле Земли недоступны"
        
        state = data.get('state', '')
        time_left = data.get('time_left', '')
        is_day = data.get('is_day', False)
        
        icon = "☀️" if is_day else "🌙"
        state_name = "День" if is_day else "Ночь"
        
        return f"{icon} **Цикл Земли**\n\nСостояние: {state_name}\n⏰ До смены: {time_left}"
    
    elif data_type == 'venus_weather':
        if not data:
            return "🌡️ Данные о погоде на Венере недоступны"
        
        state = data.get('state', '')
        time_left = data.get('time_left', '')
        is_warm = data.get('is_warm', False)
        
        icon = "☀️" if is_warm else "❄️"
        state_name = "Тепло" if is_warm else "Холодно"
        
        return f"{icon} **Погода на Венере**\n\nСостояние: {state_name}\n⏰ До смены: {time_left}"
    
    elif data_type == 'deimos_cycle':
        if not data:
            return "🕷️ Данные о цикле Деймоса недоступны"
        
        state = data.get('state', '')
        time_left = data.get('time_left', '')
        is_vome = data.get('is_vome', False)
        
        icon = "🟢" if is_vome else "🔴"
        state_name = "Воме" if is_vome else "Фасс"
        
        return f"{icon} **Цикл Деймоса**\n\nСостояние: {state_name}\n⏰ До смены: {time_left}"
    
    elif data_type == 'duviri_mood':
        if not data:
            return "🎭 Данные о настроении в Дувири недоступны"
        
        mood = data.get('mood', '')
        time_left = data.get('time_left', '')
        
        mood_emojis = {
            'joy': '😊',
            'envy': '💚',
            'fear': '😱',
            'anger': '😡',
            'sorrow': '😢'
        }
        
        mood_emoji = mood_emojis.get(mood.lower(), '🎭')
        
        return f"{mood_emoji} **Настроение Дувири**\n\nСостояние: {mood}\n⏰ До смены: {time_left}"
    
    elif data_type == 'ergo_glast':
        if not data or not data.get('inventory'):
            return "🛍️ Эрго Гласт сейчас не предлагает товаров"
        
        message = "🛒 **Эрго Гласт**\n\n"
        message += f"⏰ Обновление: {data.get('expiry', '')}\n\n"
        message += "**📦 Доступные товары:**\n"
        
        for item in data.get('inventory', [])[:5]:
            item_name = item.get('name', 'Неизвестно')
            cost = item.get('cost', {})
            item_type = item.get('type', '')
            
            message += f"• **{item_name}**\n"
            
            if cost.get('credits'):
                message += f"  💰 {cost['credits']} кредитов\n"
            if cost.get('plat'):
                message += f"  💎 {cost['plat']} платины\n"
            
            # Характеристики оружия
            if 'stats' in item:
                stats = parse_weapon_stats(item)
                if stats:
                    message += f"  {stats}\n"
            
            message += "\n"
        
        return message
    
    elif data_type == 'eleonora':
        if not data or not data.get('inventory'):
            return "🛍️ Элеонора сейчас не предлагает товаров"
        
        message = "🛒 **Элеонора**\n\n"
        message += f"⏰ Обновление: {data.get('expiry', '')}\n\n"
        message += "**📦 Доступные товары:**\n"
        
        for item in data.get('inventory', [])[:5]:
            item_name = item.get('name', 'Неизвестно')
            cost = item.get('cost', {})
            item_type = item.get('type', '')
            
            message += f"• **{item_name}**\n"
            
            if cost.get('credits'):
                message += f"  💰 {cost['credits']} кредитов\n"
            if cost.get('plat'):
                message += f"  💎 {cost['plat']} платины\n"
            
            if 'stats' in item:
                stats = parse_weapon_stats(item)
                if stats:
                    message += f"  {stats}\n"
            
            message += "\n"
        
        return message
    
    elif data_type == 'special_reward':
        if not data:
            return ""
        
        # Для реакторов и катализаторов
        message = "⚡ **Специальная награда!**\n\n"
        
        if data.get('type') == 'reactor':
            message += "🔧 **Реактор Орокин** доступен!\n"
        elif data.get('type') == 'catalyst':
            message += "💫 **Катализатор Орокин** доступен!\n"
        
        message += f"📍 {data.get('node', '')}\n"
        message += f"⏰ Доступно до: {data.get('expiry', '')}\n"
        
        return message
    
    return "Неизвестное уведомление"
