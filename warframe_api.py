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
        """
        Получение данных об Арбитраже из официального API Warframe
        """
        data = await WarframeAPI.fetch_data("arbitration")
        if data:
            # Проверяем, что данные не expired
            if data.get('expired', True):
                return None
            
            # Проверяем, что узел не пустой и не SolNode000
            node = data.get('node', '')
            if not node or node == 'SolNode000':
                return None
            
            # Извлекаем данные
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
        """
        Парсит ближайшую миссию Арбитража из блока "Next Occurrence" на browse.wf
        Используется как резервный источник, если официальное API недоступно
        """
        url = "https://browse.wf/arbys"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None

                    html = await response.text()

                    # Ищем блок "Next Occurrence"
                    next_occurrence_match = re.search(
                        r'Next Occurrence\s*</?strong>?\s*</?h2>?\s*<ul>(.*?)</ul>',
                        html,
                        re.DOTALL | re.IGNORECASE
                    )
                    
                    if not next_occurrence_match:
                        # Пробуем другой вариант поиска
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
                    
                    # Парсим детали миссии
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
