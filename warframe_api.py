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
            return {
                'active': data.get('active', False),
                'location': data.get('location', 'Неизвестно'),
                'inventory': data.get('inventory', []),
                'end': data.get('expiry', ''),  # Исправлено: expiry вместо end
                'start': data.get('activation', ''),
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
        """Получение информации о вторжениях с правильной структурой"""
        data = await WarframeAPI.fetch_data("invasions")
        if data:
            invasions = []
            for invasion in data:
                try:
                    # Пропускаем завершенные вторжения
                    if invasion.get('completed', False):
                        continue
                    
                    attacker = invasion.get('attacker', {})
                    defender = invasion.get('defender', {})
                    
                    # Получаем названия фракций из правильных полей
                    attacker_name = attacker.get('faction', 'Неизвестно')
                    defender_name = defender.get('faction', 'Неизвестно')
                    
                    # Получаем награды
                    attacker_reward = attacker.get('reward', {})
                    defender_reward = defender.get('reward', {})
                    
                    # Извлекаем предметы из наград
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
                    
                    # Определяем, есть ли особые награды
                    has_reactor = False
                    has_catalyst = False
                    
                    all_items = attacker_items + defender_items
                    for item in all_items:
                        if 'reactor' in item.lower() or 'реактор' in item.lower():
                            has_reactor = True
                        if 'catalyst' in item.lower() or 'катализатор' in item.lower():
                            has_catalyst = True
                    
                    # Формируем описание награды
                    reward_desc = []
                    if attacker_items:
                        reward_desc.append(f"🔵 {attacker_name}: {', '.join(attacker_items[:3])}")
                    if defender_items:
                        reward_desc.append(f"🔴 {defender_name}: {', '.join(defender_items[:3])}")
                    
                    # Добавляем особые отметки
                    if has_reactor:
                        reward_desc.append("⚡ **РЕАКТОР ОРОКИН!**")
                    if has_catalyst:
                        reward_desc.append("🔧 **КАТАЛИЗАТОР ОРОКИН!**")
                    
                    invasions.append({
                        'id': invasion.get('id', ''),
                        'node': invasion.get('node', 'Неизвестно'),
                        'planet': invasion.get('nodeKey', '').split('/')[0] if '/' in invasion.get('nodeKey', '') else '',
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
                        'count': invasion.get('count', 0)
                    })
                except Exception as e:
                    print(f"⚠️ Error parsing invasion: {e}")
                    continue
            
            return invasions
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
                'tier': data.get('tier', 'Обычный'),
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
                'missions': data.get('variants', []),  # Исправлено: variants вместо missions
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
        # Венера временно недоступна
        return None
    
    @staticmethod
    async def get_deimos_cycle() -> Optional[Dict]:
        # Деймос временно недоступен
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
        # Эрго Гласт временно недоступен
        return None
    
    @staticmethod
    async def get_eleonora() -> Optional[Dict]:
        # Элеонора временно недоступна
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
        
        character_name = data.get('character', "Baro Ki'Teer")
        message = f"🧛 **{character_name}**\n"
        message += f"📍 **Местоположение:** {data.get('location', 'Неизвестно')}\n"
        message += f"⏰ **Доступен до:** {data.get('end', 'Неизвестно')}\n\n"
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
        
        # Фильтруем вторжения с нормальным прогрессом
        active_invasions = [inv for inv in data if inv.get('completion', 0) >= 0]
        
        if not active_invasions:
            return "🚫 Нет активных вторжений"
        
        for invasion in active_invasions[:10]:
            node = invasion.get('node', 'Неизвестно')
            planet = invasion.get('planet', '')
            
            # Получаем названия сторон (теперь правильно!)
            attacker_name = invasion.get('attacker', {}).get('name', 'Неизвестно')
            defender_name = invasion.get('defender', {}).get('name', 'Неизвестно')
            
            # Получаем прогресс
            completion = invasion.get('completion', 0)
            if completion < 0:
                completion = 0
                
            # Форматируем локацию
            location = f"{node} ({planet})" if planet else node
            
            message += f"📍 **{location}**\n"
            message += f"⚔️ {attacker_name} vs {defender_name}\n"
            message += f"📊 Прогресс: {completion:.1f}%\n"
            
            # Добавляем информацию о наградах
            reward_desc = invasion.get('reward_description', '')
            if reward_desc:
                message += f"🎁 {reward_desc}\n"
            
            # Добавляем особые отметки
            if invasion.get('has_reactor'):
                message += "⚡ **РЕАКТОР ОРОКИН ДОСТУПЕН!**\n"
            if invasion.get('has_catalyst'):
                message += "🔧 **КАТАЛИЗАТОР ОРОКИН ДОСТУПЕН!**\n"
            
            # Добавляем время
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
        message += f"🎯 **Тип миссии:** {data.get('mission_type', data.get('type', 'Неизвестно'))}\n"
        message += f"👾 **Враг:** {data.get('enemy', 'Неизвестно')}\n"
        message += f"⭐ **Тир карты:** {data.get('tier', 'Обычный')}\n"
        message += f"⏰ **Доступен до:** {data.get('expiry', 'Неизвестно')}\n"
        
        if data.get('archwing'):
            message += "🛸 **Арчвинг активен**\n"
        if data.get('dark_sector'):
            message += "🌑 **Темный сектор**\n"
        
        return message
    
    elif data_type == 'archon':
        if not data:
            return "🚫 Охота на Архонтов сейчас недоступна"
        
        message = "🔥 **Охота на Архонтов**\n\n"
        message += f"👾 Босс: {data['boss']}\n"
        message += f"⚔️ Фракция: {data['faction']}\n"
        message += f"⏰ Доступна до: {data['expiry']}\n\n"
        message += "**📋 Миссии:**\n"
        
        for variant in data.get('missions', []):
            message += f"• {variant.get('node', '')} - {variant.get('modifier', '')}\n"
            message += f"  {variant.get('missionType', '')}\n"
        
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
            
            message += f"📍 **{mission.get('node', 'Неизвестно')}**\n"
            message += f"🎯 {mission.get('type', 'Неизвестно')} - {mission.get('faction', '')}\n"
            
            if reward:
                reward_name = reward.get('asString', '')
                reward_credits = reward.get('credits', 0)
                if reward_name:
                    message += f"🎁 Награда: {reward_name} ({reward_credits}💰)\n"
            
            if alert.get('eta'):
                message += f"⏰ {alert['eta']}\n"
            message += "\n"
        
        return message
    
    elif data_type == 'earth_cycle':
        if not data:
            return "🌍 Данные о цикле Земли недоступны"
        
        is_day = data.get('is_day', False)
        time_left = data.get('time_left', '')
        
        icon = "☀️" if is_day else "🌙"
        state_name = "День" if is_day else "Ночь"
        
        return f"{icon} **Цикл Земли**\n\nСостояние: {state_name}\n⏰ До смены: {time_left}"
    
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
    
    return "Неизвестное уведомление"


# ==============================================
# ТЕСТОВЫЙ СКРИПТ ДЛЯ ПРОВЕРКИ API
# ==============================================

async def test_invasions():
    """Тестирование получения вторжений с выводом полной структуры"""
    print("=" * 60)
    print("🔍 ТЕСТИРОВАНИЕ API ВТОРЖЕНИЙ")
    print("=" * 60)
    
    url = "https://api.warframestat.us/pc/invasions"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"\n✅ Успешно получено {len(data)} вторжений\n")
                    
                    if data:
                        # Показываем первое вторжение полностью
                        print("📋 ПЕРВОЕ ВТОРЖЕНИЕ (полная структура):")
                        print("-" * 60)
                        print(json.dumps(data[0], indent=2, ensure_ascii=False))
                        print("-" * 60)
                        
                        # Показываем все ключи
                        print("\n🔑 КЛЮЧИ ПЕРВОГО ВТОРЖЕНИЯ:")
                        print(f"  {list(data[0].keys())}")
                        
                        # Показываем структуру attacker
                        if 'attacker' in data[0]:
                            print("\n🔑 КЛЮЧИ ATTACKER:")
                            print(f"  {list(data[0]['attacker'].keys())}")
                            print(f"  Содержимое: {data[0]['attacker']}")
                        
                        # Показываем структуру defender
                        if 'defender' in data[0]:
                            print("\n🔑 КЛЮЧИ DEFENDER:")
                            print(f"  {list(data[0]['defender'].keys())}")
                            print(f"  Содержимое: {data[0]['defender']}")
                        
                        # Показываем все вторжения в кратком виде
                        print("\n" + "=" * 60)
                        print("📊 ВСЕ АКТИВНЫЕ ВТОРЖДЕНИЯ:")
                        print("=" * 60)
                        
                        for i, inv in enumerate(data[:10], 1):
                            if inv.get('completed', False):
                                continue
                                
                            node = inv.get('node', 'Неизвестно')
                            completion = inv.get('completion', 0)
                            
                            attacker = inv.get('attacker', {})
                            defender = inv.get('defender', {})
                            attacker_name = attacker.get('faction', 'Неизвестно')
                            defender_name = defender.get('faction', 'Неизвестно')
                            
                            # Получаем награды
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
                            
                            print(f"\n{i}. 📍 {node}")
                            print(f"   ⚔️ {attacker_name} vs {defender_name}")
                            print(f"   📊 Прогресс: {completion:.1f}%")
                            if attacker_items:
                                print(f"   🔵 Награда {attacker_name}: {', '.join(attacker_items[:3])}")
                            if defender_items:
                                print(f"   🔴 Награда {defender_name}: {', '.join(defender_items[:3])}")
                            if inv.get('eta'):
                                print(f"   ⏰ {inv.get('eta')}")
                        
                        # Проверяем наличие реакторов/катализаторов
                        print("\n" + "=" * 60)
                        print("🔍 ПОИСК РЕАКТОРОВ И КАТАЛИЗАТОРОВ:")
                        print("=" * 60)
                        
                        found_special = False
                        for inv in data:
                            if inv.get('completed', False):
                                continue
                                
                            attacker = inv.get('attacker', {})
                            defender = inv.get('defender', {})
                            
                            attacker_reward = attacker.get('reward', {})
                            defender_reward = defender.get('reward', {})
                            
                            all_items = []
                            if 'countedItems' in attacker_reward:
                                for item in attacker_reward['countedItems']:
                                    all_items.append(item.get('type', ''))
                            if 'countedItems' in defender_reward:
                                for item in defender_reward['countedItems']:
                                    all_items.append(item.get('type', ''))
                            
                            for item in all_items:
                                if 'reactor' in item.lower() or 'catalyst' in item.lower():
                                    found_special = True
                                    print(f"\n📍 {inv.get('node', 'Неизвестно')}")
                                    print(f"   🎁 {item}")
                        
                        if not found_special:
                            print("\n❌ Реакторов или катализаторов не найдено")
                        
                    else:
                        print("❌ Нет данных о вторжениях")
                        
                else:
                    print(f"❌ Ошибка: {response.status}")
                    
    except Exception as e:
        print(f"❌ Исключение: {e}")
        import traceback
        traceback.print_exc()


async def test_all_endpoints():
    """Тестирование всех эндпоинтов"""
    print("\n" + "=" * 60)
    print("🔍 ТЕСТИРОВАНИЕ ВСЕХ ЭНДПОИНТОВ")
    print("=" * 60)
    
    endpoints = [
        ("voidTrader", "Торговец из Бездны"),
        ("fissures", "Разрывы Бездны"),
        ("invasions", "Вторжения"),
        ("sortie", "Сортировка"),
        ("arbitration", "Арбитраж"),
        ("archonHunt", "Охота на Архонтов"),
        ("steelPath", "Стальной Путь"),
        ("alerts", "Тревоги"),
        ("earthCycle", "Цикл Земли"),
        ("duviriCycle", "Дувири")
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint, name in endpoints:
            try:
                url = f"{WARFRAME_API_URL}/{endpoint}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data:
                            if isinstance(data, list):
                                print(f"✅ {name}: {len(data)} записей")
                                if data:
                                    print(f"   Ключи: {list(data[0].keys())[:5]}...")
                            else:
                                print(f"✅ {name}: {len(data)} полей")
                                print(f"   Ключи: {list(data.keys())[:5]}...")
                        else:
                            print(f"⚠️ {name}: Пустой ответ")
                    else:
                        print(f"❌ {name}: HTTP {response.status}")
            except Exception as e:
                print(f"❌ {name}: Ошибка - {e}")


def run_tests():
    """Запуск всех тестов"""
    print("\n🚀 ЗАПУСК ТЕСТОВ API")
    print("=" * 60)
    
    # Запускаем тест вторжений
    asyncio.run(test_invasions())
    
    # Запускаем тест всех эндпоинтов
    asyncio.run(test_all_endpoints())
    
    print("\n" + "=" * 60)
    print("✅ ТЕСТЫ ЗАВЕРШЕНЫ")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
