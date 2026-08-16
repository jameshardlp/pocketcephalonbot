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
    """Меню настроек"""
    keyboard = [
        [InlineKeyboardButton("⚙️ Основные уведомления", callback_data='settings_main')],
        [InlineKeyboardButton("🌍 Циклы и погода", callback_data='settings_cycles')],
        [InlineKeyboardButton("🛒 Торговцы", callback_data='settings_traders')],
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_status_buttons(user_settings, category='main'):
    """Создание кнопок с статусом уведомлений"""
    if category == 'main':
        statuses = {
            'notify_baro': '🧛 Торговец из Бездны',
            'notify_fissures': '💠 Разрывы Бездны',
            'notify_invasions': '⚔️ Вторжения',
            'notify_sortie': '🎯 Сортировка',
            'notify_arbitration': '⚡ Арбитраж',
            'notify_archon': '🔥 Охота на Архонтов',
            'notify_steel_path': '🗡️ Стальной Путь',
            'notify_alerts': '🚨 Тревоги',
            'notify_reactor': '⚡ Реакторы Орокин',
            'notify_catalyst': '🔧 Катализаторы Орокин'
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
            'notify_ergo_glast': '🛒 Эрго Гласт',
            'notify_eleonora': '🛒 Элеонора'
        }
    else:
        statuses = {}
    
    keyboard = []
    for key, name in statuses.items():
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
        [InlineKeyboardButton("🎯 Сортировка", callback_data='info_sortie')],
        [InlineKeyboardButton("⚡ Арбитраж", callback_data='info_arbitration')],
        [InlineKeyboardButton("🔥 Охота на Архонтов", callback_data='info_archon')],
        [InlineKeyboardButton("🗡️ Стальной Путь", callback_data='info_steel_path')],
        [InlineKeyboardButton("🚨 Тревоги", callback_data='info_alerts')],
        [InlineKeyboardButton("🌍 Циклы и погода", callback_data='info_cycles')],
        [InlineKeyboardButton("🛒 Торговцы", callback_data='info_traders')],
        [InlineKeyboardButton("📊 Вся информация", callback_data='info_all')],
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_cycle_menu():
    """Меню циклов"""
    keyboard = [
        [InlineKeyboardButton("🌍 Цикл Земли", callback_data='info_earth_cycle')],
        [InlineKeyboardButton("🌡️ Погода Венеры", callback_data='info_venus_weather')],
        [InlineKeyboardButton("🕷️ Цикл Деймоса", callback_data='info_deimos_cycle')],
        [InlineKeyboardButton("🎭 Настроение Дувири", callback_data='info_duviri_mood')],
        [InlineKeyboardButton("🔙 Назад", callback_data='get_info')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_trader_menu():
    """Меню торговцев"""
    keyboard = [
        [InlineKeyboardButton("🛒 Эрго Гласт", callback_data='info_ergo_glast')],
        [InlineKeyboardButton("🛒 Элеонора", callback_data='info_eleonora')],
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