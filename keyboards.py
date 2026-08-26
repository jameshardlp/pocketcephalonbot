from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu():
    """Главное меню бота"""
    keyboard = [
        [InlineKeyboardButton("⚙️ Настройки", callback_data='settings')],
        [InlineKeyboardButton("📊 Получить информацию", callback_data='get_info')],
        [InlineKeyboardButton("📱 Виджет", callback_data='widget')],
        [InlineKeyboardButton("❓ Помощь", callback_data='help')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_settings_menu():
    """Меню настроек - категории"""
    keyboard = [
        [InlineKeyboardButton("⚙️ Основные уведомления", callback_data='settings_main')],
        [InlineKeyboardButton("🌍 Циклы и погода", callback_data='settings_cycles')],
        [InlineKeyboardButton("🛒 Торговцы", callback_data='settings_traders')],
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_status_buttons(user_settings, category='main'):
    """
    Кнопки для включения/выключения уведомлений
    category: 'main', 'cycles', 'traders'
    """
    if category == 'main':
        statuses = {
            'notify_baro': '🧛 Торговец из Бездны',
            'notify_fissures': '💠 Разрывы Бездны',
            'notify_invasions': '⚔️ Вторжения',
            'notify_sortie': '🎯 Вылазка',
            'notify_arbitration': '⚡ Арбитраж',
            'notify_archon': '🔥 Охота на Архонтов',
            'notify_steel_path': '🗡️ Стальной Путь',
            'notify_alerts': '🚨 Тревоги'
        }
    elif category == 'cycles':
        statuses = {
            'notify_earth_cycle': '🌍 Цикл Земли',
            'notify_venus_weather': '🌡️ Погода Венеры',
            'notify_deimos_cycle': '🕷️ Цикл Деймоса',
            'notify_duviri_mood': '🎭 Настроение Дувири'
        }
    elif category == 'traders':
        statuses = {
            'notify_ergo_glast': '🛒 Эрго Гласт (Реле)',
            'notify_cavalero': '🛒 Кавалеро (Зариман)',
            'notify_eleonora': '🛒 Элеонора (Хёльвания)',
            'notify_nightwave': '🌙 Ночная Волна'
        }
    else:
        statuses = {}
    
    keyboard = []
    for key, name in statuses.items():
        # Получаем статус из словаря, по умолчанию True
        status = user_settings.get(key, True)
        status_text = "✅" if status else "❌"
        keyboard.append([InlineKeyboardButton(
            f"{status_text} {name}",
            callback_data=f'toggle_{key}'
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data='settings')])
    return InlineKeyboardMarkup(keyboard)

def get_info_menu():
    """Меню получения информации"""
    keyboard = [
        [InlineKeyboardButton("🧛 Торговец из Бездны", callback_data='info_baro')],
        [InlineKeyboardButton("💠 Разрывы Бездны", callback_data='info_fissures')],
        [InlineKeyboardButton("⚔️ Вторжения", callback_data='info_invasions')],
        [InlineKeyboardButton("🎯 Вылазка", callback_data='info_sortie')],
        [InlineKeyboardButton("⚡ Арбитраж", callback_data='info_arbitration')],
        [InlineKeyboardButton("🔥 Охота на Архонтов", callback_data='info_archon')],
        [InlineKeyboardButton("🗡️ Стальной Путь", callback_data='info_steel_path')],
        [InlineKeyboardButton("🚨 Тревоги", callback_data='info_alerts')],
        [InlineKeyboardButton("🌍 Циклы", callback_data='info_cycles')],
        [InlineKeyboardButton("🛒 Торговцы", callback_data='info_traders')],
        [InlineKeyboardButton("📊 Вся информация", callback_data='info_all')],
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_cycle_menu():
    """Меню выбора циклов"""
    keyboard = [
        [InlineKeyboardButton("🌍 Цикл Земли", callback_data='info_earth_cycle')],
        [InlineKeyboardButton("🌡️ Погода Венеры", callback_data='info_venus_weather')],
        [InlineKeyboardButton("🕷️ Цикл Деймоса", callback_data='info_deimos_cycle')],
        [InlineKeyboardButton("🎭 Настроение Дувири", callback_data='info_duviri_mood')],
        [InlineKeyboardButton("🔙 Назад", callback_data='get_info')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_trader_menu():
    """Меню выбора торговцев"""
    keyboard = [
        [InlineKeyboardButton("🛒 Эрго Гласт (Реле)", callback_data='info_ergo_glast')],
        [InlineKeyboardButton("🛒 Кавалеро (Зариман)", callback_data='info_cavalero')],
        [InlineKeyboardButton("🛒 Элеонора (Хёльвания)", callback_data='info_eleonora')],
        [InlineKeyboardButton("🌙 Ночная Волна", callback_data='info_nightwave')],
        [InlineKeyboardButton("🔙 Назад", callback_data='get_info')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_widget_menu():
    """Меню виджета"""
    keyboard = [
        [InlineKeyboardButton("📱 Получить ссылку на виджет", callback_data='get_widget')],
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirmation_menu(action: str, item_name: str):
    """
    Меню подтверждения действия
    action: 'reset_settings', 'clear_history' и т.д.
    """
    keyboard = [
        [InlineKeyboardButton("✅ Да", callback_data=f'confirm_{action}')],
        [InlineKeyboardButton("❌ Нет", callback_data='back_to_settings')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_paginated_menu(items: list, page: int = 0, items_per_page: int = 5, prefix: str = 'item'):
    """
    Создание пагинированного меню для списка элементов
    """
    if not items:
        return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]])
    
    total_pages = (len(items) + items_per_page - 1) // items_per_page
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(items))
    
    keyboard = []
    for i in range(start_idx, end_idx):
        item = items[i]
        if isinstance(item, dict):
            name = item.get('name', str(i))
            callback = f"{prefix}_{item.get('id', i)}"
        else:
            name = str(item)
            callback = f"{prefix}_{i}"
        keyboard.append([InlineKeyboardButton(name, callback_data=callback)])
    
    # Кнопки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f'{prefix}_page_{page-1}'))
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='ignore'))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f'{prefix}_page_{page+1}'))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')])
    return InlineKeyboardMarkup(keyboard)

def get_error_menu(error_message: str):
    """
    Меню для отображения ошибки с кнопкой возврата
    """
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)
