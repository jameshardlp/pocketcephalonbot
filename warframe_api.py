import aiohttp
import asyncio
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any

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
                    'ducats': item.get('ducats', 0),
                    'credits': item.get('credits', 0)
                })
            
            return {
                'active': len(inventory) > 0,
                'location': data.get('location', 'Неизвестно'),
                'inventory': inventory,
                'expiry': data.get('expiry', ''),
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
                                'is_storm': fissure.get('isStorm', False)
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
                    
                    defender_items = []
                    if 'countedItems' in defender_reward:
                        for item in defender_reward['countedItems']:
                            defender_items.append(item.get('type', ''))
                    
                    has_reactor = False
                    has_catalyst = False
                    
                    all_items = attacker_items + defender_items
                    for item in all_items:
                        if 'reactor' in item.lower():
                            has_reactor = True
                        if 'catalyst' in item.lower():
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
                        'attacker': {
                            'name': attacker_name,
                            'faction': attacker.get('factionKey', '')
                        },
                        'defender': {
                            'name': defender_name,
                            'faction': defender.get('factionKey', '')
                        },
                        'completion': invasion.get('completion', 0),
                        'reward_description': '\n'.join(reward_desc) if reward_desc else 'Нет данных',
                        'has_reactor': has_reactor,
                        'has_catalyst': has_catalyst,
                        'eta': invasion.get('eta', ''),
                        'description': invasion.get('desc', ''),
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
                    'mission_type': variant.get('missionType', 'Неизвестно')
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
            if data.get('expired', True):
                return None
            node = data.get('node', '')
            if not node or node == 'SolNode000':
                return None
            return {
                'node': node,
                'type': data.get('type', 'Неизвестно'),
                'enemy': data.get('enemy', 'Неизвестно'),
                'expiry': data.get('expiry', 'Неизвестно'),
                'archwing': data.get('archwing', False),
                'sharkwing': data.get('sharkwing', False),
                'source': 'api'
            }
        return None
    
    @staticmethod
    async def get_arbitration_from_browse() -> Optional[Dict]:
        url = "https://browse.wf/arbys"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None
                    html = await response.text()
                    next_occurrence_match = re.search(
                        r'Next Occurrence\s*</?strong>?\s*</?h2>?\s*<ul>(.*?)</ul>',
                        html,
                        re.DOTALL | re.IGNORECASE
                    )
                    if not next_occurrence_match:
                        next_occurrence_match = re.search(
                            r'Next Occurrence\s*</?strong>?\s*</?h2>?\s*(.*?)(?=<h2|###|$)',
                            html,
                            re.DOTALL | re.IGNORECASE
                        )
                    if not next_occurrence_match:
                        return None
                    block_content = next_occurrence_match.group(1)
                    lines = block_content.strip().split('\n')
                    clean_lines = []
                    for line in lines:
                        clean = re.sub(r'<[^>]+>', '', line).strip()
                        if clean and '|' in clean:
                            clean_lines.append(clean)
                    if not clean_lines:
                        return None
                    first_mission = clean_lines[0]
                    parts = first_mission.split(' | ', 1)
                    if len(parts) != 2:
                        return None
                    date_time_str, mission_details = parts[0], parts[1]
                    mission_parts = mission_details.split(' @ ')
                    if len(mission_parts) != 2:
                        return None
                    left_part = mission_parts[0].strip()
                    right_part = mission_parts[1].strip()
                    node_planet_bonus = right_part.split(' (', 1)
                    node_planet = node_planet_bonus[0].strip()
                    bonus = f"({node_planet_bonus[1]}" if len(node_planet_bonus) > 1 else ''
                    if ', ' in node_planet:
                        node, planet = node_planet.split(', ', 1)
                    else:
                        node = node_planet
                        planet = ''
                    bonus = bonus.replace(')', '').strip() if bonus else ''
                    return {
                        'datetime': date_time_str,
                        'type': left_part,
                        'node': node.strip(),
                        'planet': planet.strip(),
                        'bonus': bonus,
                        'source': 'browse.wf'
                    }
        except Exception as e:
            print(f"Error parsing browse.wf: {e}")
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
                    'archwing': mission.get('archwingRequired', False)
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
                'remaining': data.get('remaining', ''),
                'expiry': data.get('expiry', '')
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
                            mission = alert.get('mission', {})
                            reward = mission.get('reward', {})
                            counted_items = []
                            if 'countedItems' in reward:
                                for item in reward['countedItems']:
                                    counted_items.append(f"{item.get('count', '')}x {item.get('type', '')}")
                            alerts.append({
                                'id': alert.get('id', ''),
                                'node': mission.get('node', 'Неизвестно'),
                                'type': mission.get('type', 'Неизвестно'),
                                'faction': mission.get('faction', 'Неизвестно'),
                                'reward_items': ', '.join(counted_items) if counted_items else 'Нет данных',
                                'credits': reward.get('credits', 0),
                                'expiry': alert.get('expiry', '')
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
        data = await WarframeAPI.fetch_data("vallisCycle")
        if data:
            return {
                'state': data.get('state', ''),
                'time_left': data.get('timeLeft', ''),
                'is_warm': data.get('isWarm', False)
            }
        return None
    
    @staticmethod
    async def get_deimos_cycle() -> Optional[Dict]:
        data = await WarframeAPI.fetch_data("cambionCycle")
        if data:
            return {
                'state': data.get('state', ''),
                'time_left': data.get('timeLeft', '')
            }
        return None
    
    @staticmethod
    async def get_duviri_mood() -> Optional[Dict]:
        data = await WarframeAPI.fetch_data("duviriCycle")
        if data:
            return {
                'mood': data.get('state', ''),
                'time_left': data.get('timeLeft', '')
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
                    }
                })
            return {
                'season': data.get('season', ''),
                'phase': data.get('phase', 0),
                'expiry': data.get('expiry', 'Неизвестно'),
                'offers': offers
            }
        return None
    
    @staticmethod
    async def get_ergo_glast() -> Optional[Dict]:
        return None
    
    @staticmethod
    async def get_cavalero() -> Optional[Dict]:
        return None
    
    @staticmethod
    async def get_eleonora() -> Optional[Dict]:
        return None


# ==============================================
# ФУНКЦИЯ ФОРМАТИРОВАНИЯ УВЕДОМЛЕНИЙ
# ==============================================

def format_notification(data_type: str, data) -> str:
    """Форматирование уведомлений для отправки в Telegram"""
    
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
            message += "\n"
        
        return message
    
    elif data_type == 'invasions':
        if not data:
            return "⚔️ Активных вторжений нет"
        
        message = "⚔️ **Активные вторжения**\n\n"
        
        active_invasions = [inv for inv in data if inv.get('completion', 0) >= 0 and inv.get('completion', 0) < 100]
        
        if not active_invasions:
            return "⚔️ Все вторжения завершены! Новые появятся позже."
        
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
        
        return message
    
    elif data_type == 'arbitration':
        if not data:
            return "⚡ Арбитраж сейчас недоступен"
        
        message = "⚡ **Арбитраж**\n\n"
        
        if data.get('source') == 'browse.wf':
            message += f"🕐 **Время:** {data.get('datetime', 'Неизвестно')}\n"
            message += f"🎯 **Тип:** {data.get('type', 'Неизвестно')}\n"
            message += f"📍 **Узел:** {data.get('node', 'Неизвестно')}"
            if data.get('planet'):
                message += f" ({data.get('planet')})"
            message += "\n"
            if data.get('bonus'):
                message += f"💰 **Бонус:** {data.get('bonus')}\n"
        else:
            message += f"📍 **Узел:** {data.get('node', 'Неизвестно')}\n"
            message += f"🎯 **Тип миссии:** {data.get('type', 'Неизвестно')}\n"
            message += f"👾 **Враг:** {data.get('enemy', 'Неизвестно')}\n"
            message += f"⏰ **Доступен до:** {data.get('expiry', 'Неизвестно')}\n"
            
            if data.get('archwing'):
                message += "🛸 **Арчвинг активен**\n"
            if data.get('sharkwing'):
                message += "🦈 **Шарквинг активен**\n"
        
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
        
        return message
    
    elif data_type == 'steel_path':
        if not data:
            return "🗡️ Стальной Путь сейчас неактивен"
        
        message = "🗡️ **Стальной Путь**\n\n"
        reward = data.get('current_reward', {})
        if reward:
            message += f"🎁 **Текущая награда:** {reward.get('name', 'Неизвестно')}\n"
            message += f"⏰ **Доступно:** {data.get('remaining', 'Неизвестно')}\n"
        else:
            message += "Текущая награда не определена\n"
        
        return message
    
    elif data_type == 'alerts':
        if not data:
            return "🚨 Активных тревог нет"
        
        message = "🚨 **Активные тревоги**\n\n"
        
        for alert in data[:10]:
            message += f"📍 **{alert.get('node', 'Неизвестно')}**\n"
            message += f"🎯 {alert.get('type', 'Неизвестно')}"
            if alert.get('faction'):
                message += f" - {alert.get('faction', '')}"
            message += "\n"
            
            reward_items = alert.get('reward_items', '')
            credits = alert.get('credits', 0)
            if reward_items and reward_items != 'Нет данных':
                message += f"🎁 Награда: {reward_items}"
                if credits > 0:
                    message += f" (+{credits}💰)"
                message += "\n"
            
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
        
        state = data.get('state', '')
        time_left = data.get('time_left', 'Неизвестно')
        
        icon = "🟢" if "vome" in state.lower() else "🔴"
        state_name = "Воме" if "vome" in state.lower() else "Фасс"
        
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
    
    elif data_type == 'nightwave':
        if not data:
            return "🌙 Ночная Волна сейчас недоступна"
        
        message = "🌙 **Ночная Волна**\n\n"
        message += f"📅 **Сезон:** {data.get('season', 'Неизвестно')}\n"
        message += f"📊 **Фаза:** {data.get('phase', 0)}\n"
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
    
    return "Неизвестное уведомление"
