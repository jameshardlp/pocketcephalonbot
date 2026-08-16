import aiohttp
import asyncio
import json
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
            inventory = []
            for item in data.get('inventory', []):
                inventory.append({
                    'item': item.get('item', 'Неизвестно'),
                    'cost': item.get('cost', {}),
                    'ducats': item.get('cost', {}).get('ducats', 0),
                    'credits': item.get('cost', {}).get('credits', 0),
                    'type': item.get('type', '')
                })
            
            is_active = len(inventory) > 0
            
            return {
                'active': is_active,
                'location': data.get('location', 'Неизвестно'),
                'inventory': inventory,
                'expiry': data.get('expiry', ''),
                'start': data.get('activation', ''),
                'character': data.get('character', "Baro Ki'Teer")
            }
        return None
    
    @staticmethod
    async def get_fissures() -> Optional[List[Dict]]:
        data = await WarframeAPI.fetch_data("fissures")
        if data:
            result = []
            for fissure in data:
                expiry = fissure.get('expiry', '')
                if expiry:
                    try:
                        expiry_time = datetime.fromisoformat(expiry.replace('Z', '+00:00'))
                        if expiry_time > datetime.utcnow():
                            result.append({
                                'id': fissure.get('id', ''),
                                'tier': fissure.get('tier', ''),
                                'node': fissure.get('node', ''),
                                'mission_type': fissure.get('missionType', ''),
                                'enemy': fissure.get('enemy', ''),
                                'expiry': fissure.get('expiry', ''),
                                'active': True,
                                'tier_num': fissure.get('tierNum', 0),
                                'is_storm': fissure.get('isStorm', False),
                                'eta': fissure.get('eta', '')
                            })
                    except:
                        pass
            return result if result else None
        return []
    
    @staticmethod
    async def get_invasions() -> Optional[List[Dict]]:
        data = await WarframeAPI.fetch_data("invasions")
        if data:
            invasions = []
            for invasion in data:
                try:
                    if invasion.get('completed', False):
                        continue
                    
                    attacker = invasion.get('attacker', {})
                    defender = invasion.get('defender', {})
                    
                    attacker_name = attacker.get('faction', 'Неизвестно')
                    defender_name = defender.get('faction', 'Неизвестно')
                    
                    attacker_reward = attacker.get('reward', {})
                    defender_reward = defender.get('reward', {})
                    
                    attacker_items = []
                    if 'countedItems' in attacker_reward:
                        for item in attacker_reward['countedItems']:
                            attacker_items.append(item.get('type', ''))
                    if 'items' in attacker_reward:
                        for item in attacker_reward['items']:
                            attacker_items.append(item.get('type', ''))
                    
                    defender_items = []
                    if 'countedItems' in defender_reward:
                        for item in defender_reward['countedItems']:
                            defender_items.append(item.get('type', ''))
                    if 'items' in defender_reward:
                        for item in defender_reward['items']:
                            defender_items.append(item.get('type', ''))
                    
                    has_reactor = False
                    has_catalyst = False
                    
                    all_items = attacker_items + defender_items
                    for item in all_items:
                        if 'reactor' in item.lower() or 'реактор' in item.lower():
                            has_reactor = True
                        if 'catalyst' in item.lower() or 'катализатор' in item.lower():
                            has_catalyst = True
                    
                    reward_desc = []
                    if attacker_items:
                        reward_desc.append(f"🔵 {attacker_name}: {', '.join(attacker_items[:3])}")
                    if defender_items:
                        reward_desc.append(f"🔴 {defender_name}: {', '.join(defender_items[:3])}")
                    
                    if has_reactor:
                        reward_desc.append("⚡ **РЕАКТОР ОРОКИН!**")
                    if has_catalyst:
                        reward_desc.append("🔧 **КАТАЛИЗАТОР ОРОКИН!**")
                    
                    invasions.append({
                        'id': invasion.get('id', ''),
                        'node': invasion.get('node', 'Неизвестно'),
                        'planet': '',
                        'faction': invasion.get('faction', 'Неизвестно'),
                        'attacker': {
                            'name': attacker_name,
                            'faction': attacker.get('factionKey', ''),
                            'reward': attacker_reward
                        },
                        'defender': {
                            'name': defender_name,
                            'faction': defender.get('factionKey', ''),
                            'reward': defender_reward
                        },
                        'completion': invasion.get('completion', 0),
                        'reward_description': '\n'.join(reward_desc) if reward_desc else 'Нет данных',
                        'has_reactor': has_reactor,
                        'has_catalyst': has_catalyst,
                        'eta': invasion.get('eta', ''),
                        'vs': invasion.get('vs', ''),
                        'description': invasion.get('desc', ''),
                        'expiry': invasion.get('expiry', ''),
                        'start': invasion.get('activation', ''),
                        'completed': invasion.get('completed', False),
                        'required_runs': invasion.get('requiredRuns', 0),
                        'count': invasion.get('count', 0),
                        'hash': f"{invasion.get('id')}_{invasion.get('completion')}_{attacker_name}_{defender_name}"
                    })
                except Exception as e:
                    print(f"⚠️ Error parsing invasion: {e}")
                    continue
            
            return invasions if invasions else None
        return []
    
    @staticmethod
    async def get_sortie() -> Optional[Dict]:
        data = await WarframeAPI.fetch_data("sortie")
        if data:
            variants = []
            for variant in data.get('variants', []):
                variants.append({
                    'node': variant.get('node', 'Неизвестно'),
                    'modifier': variant.get('modifier', ''),
                    'mission_type': variant.get('missionType', 'Неизвестно'),
                    'faction': variant.get('faction', '')
                })
            
            if not variants:
                return None
            
            return {
                'boss': data.get('boss', 'Неизвестно'),
                'faction': data.get('faction', 'Неизвестно'),
                'variants': variants,
                'expiry': data.get('expiry', ''),
                'reward_pool': data.get('rewardPool', [])
            }
        return None
    
    @staticmethod
    async def get_arbitration() -> Optional[Dict]:
        data = await WarframeAPI.fetch_data("arbitration")
        if data:
            expired = data.get('expired', True)
            node = data.get('node', '')
            
            if expired or node == 'SolNode000' or not node:
                return None
            
            return {
                'node': data.get('node', 'Неизвестно'),
                'type': data.get('type', 'Неизвестно'),
                'enemy': data.get('enemy', 'Неизвестно'),
                'expiry': data.get('expiry', 'Неизвестно'),
                'node_key': data.get('nodeKey', ''),
                'tier': 'Обычный',
                'mission_type': data.get('type', 'Неизвестно'),
                'archwing': data.get('archwing', False),
                'dark_sector': data.get('darkSector', False)
            }
        return None
    
    @staticmethod
    async def get_archon_hunt() -> Optional[Dict]:
        data = await WarframeAPI.fetch_data("archonHunt")
        if data:
            missions = []
            for mission in data.get('missions', []):
                missions.append({
                    'node': mission.get('node', 'Неизвестно'),
                    'type': mission.get('type', 'Неизвестно'),
                    'modifier': '',
                    'faction': '',
                    'boss': '',
                    'archwing': mission.get('archwingRequired', False),
                    'dark_sector': False,
                    'expiry': ''
                })
            
            if not missions:
                return None
            
            return {
                'boss': data.get('boss', 'Неизвестно'),
                'faction': data.get('faction', 'Неизвестно'),
                'missions': missions,
                'expiry': data.get('expiry', ''),
                'reward_pool': data.get('rewardPool', [])
            }
        return None
    
    @staticmethod
    async def get_steel_path() -> Optional[Dict]:
        data = await WarframeAPI.fetch_data("steelPath")
        if data:
            if not data.get('active', False):
                return None
            
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
            alerts = []
            for alert in data:
                expiry = alert.get('expiry', '')
                if expiry:
                    try:
                        expiry_time = datetime.fromisoformat(expiry.replace('Z', '+00:00'))
                        if expiry_time > datetime.utcnow():
                            alerts.append({
                                'id': alert.get('id', ''),
                                'mission': alert.get('mission', {}),
                                'reward': alert.get('reward', {}),
                                'expiry': alert.get('expiry', ''),
                                'eta': alert.get('eta', '')
                            })
                    except:
                        pass
            return alerts if alerts else None
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
        """Погода на Венере"""
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
        """Цикл Деймоса (Фасс/Воме)"""
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
                'mood': data.get('state', ''),
                'time_left': data.get('timeLeft', ''),
                'mood_icon': data.get('moodIcon', '')
            }
        return None
    
    @staticmethod
    async def get_ergo_glast() -> Optional[Dict]:
        """Эрго Гласт - торговец в Реле"""
        data = await WarframeAPI.fetch_data("ergoGlast")
        if data and data.get('inventory'):
            inventory = []
            for item in data.get('inventory', []):
                cost = item.get('cost', {})
                
                stats = []
                if 'stats' in item:
                    for stat in item['stats']:
                        if stat.get('positive', ''):
                            stats.append(f"✅ {stat['positive']}")
                        if stat.get('negative', ''):
                            stats.append(f"❌ {stat['negative']}")
                
                inventory.append({
                    'name': item.get('name', 'Неизвестно'),
                    'type': item.get('type', ''),
                    'cost': {
                        'corrupted_holokeys': cost.get('corruptedHolokeys', 0),
                        'credits': cost.get('credits', 0),
                    },
                    'stats': '\n'.join(stats) if stats else 'Нет данных',
                    'description': item.get('description', ''),
                    'image': item.get('image', '')
                })
            
            return {
                'inventory': inventory,
                'expiry': data.get('expiry', 'Неизвестно'),
                'seller': 'Эрго Гласт'
            }
        return None
    
    @staticmethod
    async def get_cavalero() -> Optional[Dict]:
        """Кавалеро - торговец на Заримане"""
        data = await WarframeAPI.fetch_data("cavalero")
        if data and data.get('inventory'):
            inventory = []
            for item in data.get('inventory', []):
                cost = item.get('cost', {})
                
                stats = []
                if 'stats' in item:
                    for stat in item['stats']:
                        if stat.get('positive', ''):
                            stats.append(f"✅ {stat['positive']}")
                        if stat.get('negative', ''):
                            stats.append(f"❌ {stat['negative']}")
                
                inventory.append({
                    'name': item.get('name', 'Неизвестно'),
                    'type': item.get('type', ''),
                    'cost': {
                        'credits': cost.get('credits', 0),
                        'evolve': cost.get('evolve', 0),
                    },
                    'stats': '\n'.join(stats) if stats else 'Нет данных',
                    'description': item.get('description', ''),
                    'image': item.get('image', '')
                })
            
            return {
                'inventory': inventory,
                'expiry': data.get('expiry', 'Неизвестно'),
                'seller': 'Кавалеро'
            }
        return None
    
    @staticmethod
    async def get_eleonora() -> Optional[Dict]:
        """Элеонора - торговец в Хёльвании"""
        data = await WarframeAPI.fetch_data("eleonora")
        if data and data.get('inventory'):
            inventory = []
            for item in data.get('inventory', []):
                cost = item.get('cost', {})
                
                stats = []
                if 'stats' in item:
                    for stat in item['stats']:
                        if stat.get('positive', ''):
                            stats.append(f"✅ {stat['positive']}")
                        if stat.get('negative', ''):
                            stats.append(f"❌ {stat['negative']}")
                
                inventory.append({
                    'name': item.get('name', 'Неизвестно'),
                    'type': item.get('type', ''),
                    'cost': {
                        'lith_credits': cost.get('lithCredits', 0),
                    },
                    'stats': '\n'.join(stats) if stats else 'Нет данных',
                    'description': item.get('description', ''),
                    'image': item.get('image', '')
                })
            
            return {
                'inventory': inventory,
                'expiry': data.get('expiry', 'Неизвестно'),
                'seller': 'Элеонора'
            }
        return None
    
    @staticmethod
    async def get_nightwave() -> Optional[Dict]:
        data = await WarframeAPI.fetch_data("nightwave")
        if data:
            offers = []
            for offer in data.get('offers', []):
                cost = offer.get('cost', {})
                
                offers.append({
                    'name': offer.get('name', 'Неизвестно'),
                    'type': offer.get('type', ''),
                    'cost': {
                        'nightwave_credits': cost.get('nightwaveCredits', 0),
                    },
                    'description': offer.get('description', ''),
                    'image': offer.get('image', '')
                })
            
            return {
                'season': data.get('season', ''),
                'current_rank': data.get('currentRank', 0),
                'max_rank': data.get('maxRank', 30),
                'expiry': data.get('expiry', 'Неизвестно'),
                'offers': offers,
                'rewards': data.get('rewards', [])
            }
        return None

def format_notification(data_type: str, data) -> str:
    if data_type == 'baro':
        if not data or not data.get('active'):
            return "🧛 Торговец из Бездны сейчас неактивен"
        
        character_name = data.get('character', "Baro Ki'Teer")
        message = f"🧛 **{character_name}**\n"
        message += f"📍 **Местоположение:** {data.get('location', 'Неизвестно')}\n"
        message += f"⏰ **Доступен до:** {data.get('expiry', 'Неизвестно')}\n\n"
        message += "**🛍️ Инвентарь:**\n"
        
        for item in data.get('inventory', [])[:10]:
            item_name = item.get('item', 'Неизвестно')
            ducats = item.get('ducats', 0)
            credits = item.get('credits', 0)
            message += f"• {item_name} - {ducats}🪙 {credits}💰\n"
        
        return message
    
    elif data_type == 'fissures':
        if not data:
            return "💠 Активных разрывов Бездны нет"
        
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
            return "⚔️ Активных вторжений нет"
        
        message = "⚔️ **Активные вторжения**\n\n"
        
        active_invasions = [inv for inv in data if inv.get('completion', 0) >= 0 and inv.get('completion', 0) < 100]
        
        if not active_invasions:
            completed = [inv for inv in data if inv.get('completion', 0) >= 100]
            if completed:
                return "⚔️ Все вторжения завершены! Новые появятся позже."
            return "⚔️ Активных вторжений нет"
        
        for invasion in active_invasions[:10]:
            node = invasion.get('node', 'Неизвестно')
            
            attacker_name = invasion.get('attacker', {}).get('name', 'Неизвестно')
            defender_name = invasion.get('defender', {}).get('name', 'Неизвестно')
            
            completion = invasion.get('completion', 0)
            if completion < 0:
                completion = 0
                
            message += f"📍 **{node}**\n"
            message += f"⚔️ {attacker_name} vs {defender_name}\n"
            message += f"📊 Прогресс: {completion:.1f}%\n"
            
            reward_desc = invasion.get('reward_description', '')
            if reward_desc and reward_desc != 'Нет данных':
                message += f"🎁 {reward_desc}\n"
            
            if invasion.get('has_reactor'):
                message += "⚡ **РЕАКТОР ОРОКИН ДОСТУПЕН!**\n"
            if invasion.get('has_catalyst'):
                message += "🔧 **КАТАЛИЗАТОР ОРОКИН ДОСТУПЕН!**\n"
            
            if invasion.get('eta'):
                message += f"⏰ {invasion['eta']}\n"
            
            message += "\n"
        
        return message
    
    elif data_type == 'sortie':
        if not data:
            return "🎯 Вылазка сейчас недоступна"
        
        message = "🎯 **Вылазка**\n\n"
        message += f"👾 **Босс:** {data.get('boss', 'Неизвестно')}\n"
        message += f"⚔️ **Фракция:** {data.get('faction', 'Неизвестно')}\n"
        message += f"⏰ **Доступна до:** {data.get('expiry', 'Неизвестно')}\n\n"
        message += "**📋 Задания:**\n"
        
        for variant in data.get('variants', []):
            message += f"• 📍 **{variant.get('node', 'Неизвестно')}**\n"
            message += f"  🎯 {variant.get('mission_type', 'Неизвестно')}"
            if variant.get('modifier'):
                message += f" ({variant.get('modifier', '')})"
            message += "\n"
        
        if data.get('reward_pool'):
            message += f"\n**🎁 Возможные награды:**\n"
            for reward in data['reward_pool'][:5]:
                message += f"• {reward}\n"
        
        return message
    
    elif data_type == 'arbitration':
        if not data:
            return "⚡ Арбитраж сейчас недоступен"
        
        message = "⚡ **Арбитраж**\n\n"
        message += f"📍 **Узел:** {data.get('node', 'Неизвестно')}\n"
        message += f"🎯 **Тип миссии:** {data.get('mission_type', data.get('type', 'Неизвестно'))}\n"
        message += f"👾 **Враг:** {data.get('enemy', 'Неизвестно')}\n"
        message += f"⏰ **Доступен до:** {data.get('expiry', 'Неизвестно')}\n"
        
        if data.get('archwing'):
            message += "🛸 **Арчвинг активен**\n"
        if data.get('dark_sector'):
            message += "🌑 **Темный сектор**\n"
        
        return message
    
    elif data_type == 'archon':
        if not data:
            return "🔥 Охота на Архонтов сейчас недоступна"
        
        message = "🔥 **Охота на Архонтов**\n\n"
        message += f"👾 **Босс:** {data.get('boss', 'Неизвестно')}\n"
        message += f"⚔️ **Фракция:** {data.get('faction', 'Неизвестно')}\n"
        message += f"⏰ **Доступна до:** {data.get('expiry', 'Неизвестно')}\n\n"
        
        missions = data.get('missions', [])
        if missions:
            message += "**📋 Миссии:**\n\n"
            for i, mission in enumerate(missions, 1):
                node = mission.get('node', 'Неизвестно')
                mission_type = mission.get('type', 'Неизвестно')
                
                message += f"{i}. 📍 **{node}**\n"
                message += f"   🎯 {mission_type}\n"
                
                if mission.get('archwing'):
                    message += "   🛸 Арчвинг активен\n"
                message += "\n"
        else:
            message += "📋 Нет активных миссий\n"
        
        return message
    
    elif data_type == 'steel_path':
        if not data:
            return "🗡️ Стальной Путь сейчас неактивен"
        
        message = "🗡️ **Стальной Путь**\n\n"
        reward = data.get('current_reward', {})
        if reward:
            message += f"🎁 **Текущая награда:** {reward.get('name', 'Неизвестно')}\n"
            message += f"🔄 **Ротация:** {data.get('rotation', 'Неизвестно')}\n"
            message += f"⏰ **Доступно:** {data.get('remaining', 'Неизвестно')}\n"
        else:
            message += "Текущая награда не определена\n"
        
        return message
    
    elif data_type == 'alerts':
        if not data:
            return "🚨 Активных тревог нет"
        
        message = "🚨 **Активные тревоги**\n\n"
        
        for alert in data[:10]:
            mission = alert.get('mission', {})
            reward = alert.get('reward', {})
            
            message += f"📍 **{mission.get('node', 'Неизвестно')}**\n"
            message += f"🎯 {mission.get('type', 'Неизвестно')}"
            if mission.get('faction'):
                message += f" - {mission.get('faction', '')}"
            message += "\n"
            
            if reward:
                reward_name = reward.get('asString', '')
                reward_credits = reward.get('credits', 0)
                if reward_name:
                    message += f"🎁 Награда: {reward_name}"
                    if reward_credits > 0:
                        message += f" ({reward_credits}💰)"
                    message += "\n"
            
            if alert.get('eta'):
                message += f"⏰ {alert['eta']}\n"
            message += "\n"
        
        return message
    
    elif data_type == 'earth_cycle':
        if not data:
            return "🌍 Данные о цикле Земли недоступны"
        
        is_day = data.get('is_day', False)
        time_left = data.get('time_left', 'Неизвестно')
        
        icon = "☀️" if is_day else "🌙"
        state_name = "День" if is_day else "Ночь"
        
        return f"{icon} **Цикл Земли**\n\nСостояние: {state_name}\n⏰ До смены: {time_left}"
    
    elif data_type == 'venus_weather':
        if not data:
            return "🌡️ Данные о погоде на Венере недоступны"
        
        is_warm = data.get('is_warm', False)
        time_left = data.get('time_left', 'Неизвестно')
        
        icon = "☀️" if is_warm else "❄️"
        state_name = "Тепло" if is_warm else "Холодно"
        
        return f"{icon} **Погода на Венере**\n\nСостояние: {state_name}\n⏰ До смены: {time_left}"
    
    elif data_type == 'deimos_cycle':
        if not data:
            return "🕷️ Данные о цикле Деймоса недоступны"
        
        is_vome = data.get('is_vome', False)
        time_left = data.get('time_left', 'Неизвестно')
        
        icon = "🟢" if is_vome else "🔴"
        state_name = "Воме" if is_vome else "Фасс"
        
        return f"{icon} **Цикл Деймоса**\n\nСостояние: {state_name}\n⏰ До смены: {time_left}"
    
    elif data_type == 'duviri_mood':
        if not data:
            return "🎭 Данные о настроении в Дувири недоступны"
        
        mood = data.get('mood', '')
        time_left = data.get('time_left', 'Неизвестно')
        
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
            return "🛒 Эрго Гласт сейчас не предлагает товаров"
        
        message = f"🛒 **{data.get('seller', 'Эрго Гласт')}**\n"
        message += f"📍 **Реле**\n"
        message += f"⏰ **Обновление:** {data.get('expiry', 'Неизвестно')}\n\n"
        message += "**📦 Доступные товары:**\n\n"
        
        for item in data.get('inventory', [])[:5]:
            item_name = item.get('name', 'Неизвестно')
            cost = item.get('cost', {})
            stats = item.get('stats', 'Нет данных')
            
            message += f"• **{item_name}**\n"
            
            if cost.get('corrupted_holokeys'):
                message += f"  🗝️ {cost['corrupted_holokeys']} Испорченных голоключей\n"
            if cost.get('credits'):
                message += f"  💰 {cost['credits']} кредитов\n"
            
            if stats and stats != 'Нет данных':
                message += f"  📊 {stats}\n"
            
            message += "\n"
        
        return message
    
    elif data_type == 'cavalero':
        if not data or not data.get('inventory'):
            return "🛒 Кавалеро сейчас не предлагает товаров"
        
        message = f"🛒 **{data.get('seller', 'Кавалеро')}**\n"
        message += f"📍 **Зариман**\n"
        message += f"⏰ **Обновление:** {data.get('expiry', 'Неизвестно')}\n\n"
        message += "**📦 Доступные товары:**\n\n"
        
        for item in data.get('inventory', [])[:5]:
            item_name = item.get('name', 'Неизвестно')
            cost = item.get('cost', {})
            stats = item.get('stats', 'Нет данных')
            
            message += f"• **{item_name}**\n"
            
            if cost.get('credits'):
                message += f"  💰 {cost['credits']} кредитов\n"
            if cost.get('evolve'):
                message += f"  🔄 {cost['evolve']} эволюций\n"
            
            if stats and stats != 'Нет данных':
                message += f"  📊 {stats}\n"
            
            message += "\n"
        
        return message
    
    elif data_type == 'eleonora':
        if not data or not data.get('inventory'):
            return "🛒 Элеонора сейчас не предлагает товаров"
        
        message = f"🛒 **{data.get('seller', 'Элеонора')}**\n"
        message += f"📍 **Хёльвания**\n"
        message += f"⏰ **Обновление:** {data.get('expiry', 'Неизвестно')}\n\n"
        message += "**📦 Доступные товары:**\n\n"
        
        for item in data.get('inventory', [])[:5]:
            item_name = item.get('name', 'Неизвестно')
            cost = item.get('cost', {})
            stats = item.get('stats', 'Нет данных')
            
            message += f"• **{item_name}**\n"
            
            if cost.get('lith_credits'):
                message += f"  🟣 {cost['lith_credits']} кредитов заражённых личей\n"
            
            if stats and stats != 'Нет данных':
                message += f"  📊 {stats}\n"
            
            message += "\n"
        
        return message
    
    elif data_type == 'nightwave':
        if not data:
            return "🌙 Ночная Волна сейчас недоступна"
        
        message = "🌙 **Ночная Волна**\n\n"
        message += f"📅 **Сезон:** {data.get('season', 'Неизвестно')}\n"
        message += f"⭐ **Ранг:** {data.get('current_rank', 0)}/{data.get('max_rank', 30)}\n"
        message += f"⏰ **Доступно до:** {data.get('expiry', 'Неизвестно')}\n\n"
        
        offers = data.get('offers', [])
        if offers:
            message += "**🛍️ Текущие предложения:**\n\n"
            for offer in offers[:5]:
                message += f"• **{offer.get('name', 'Неизвестно')}**\n"
                cost = offer.get('cost', {})
                if cost.get('nightwave_credits'):
                    message += f"  🌙 {cost['nightwave_credits']} кредитов Ночной Волны\n"
                message += "\n"
        
        return message
    
    elif data_type == 'special_reward':
        if not data:
            return ""
        
        message = "⚡ **Специальная награда!**\n\n"
        
        if data.get('type') == 'reactor':
            message += "🔧 **Реактор Орокин** доступен!\n"
        elif data.get('type') == 'catalyst':
            message += "💫 **Катализатор Орокин** доступен!\n"
        
        message += f"📍 {data.get('node', 'Неизвестно')}\n"
        message += f"⏰ Доступно до: {data.get('expiry', 'Неизвестно')}\n"
        
        return message
    
    return "Неизвестное уведомление"
