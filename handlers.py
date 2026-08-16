from telegram import Update
from telegram.ext import ContextTypes
import asyncio
from datetime import datetime

from database import get_user, update_user_settings, generate_widget_token
from warframe_api import WarframeAPI, format_notification
from keyboards import (
    get_main_menu, get_settings_menu, get_info_menu, 
    get_status_buttons, get_trader_menu, get_cycle_menu
)
from utils import create_widget_url

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = user.id
    
    db_user = get_user(telegram_id)
    widget_token = generate_widget_token(telegram_id)
    
    welcome_message = (
        f"👋 Привет, {user.first_name}!\n\n"
        f"Я бот для отслеживания событий в Warframe.\n\n"
        f"**Что я могу:**\n"
        f"• 🧛 Торговец из Бездны (Baro Ki'Teer)\n"
        f"• 💠 Разрывы Бездны\n"
        f"• ⚔️ Вторжения (включая реакторы и катализаторы)\n"
        f"• 🎯 Вылазка\n"
        f"• ⚡ Арбитраж\n"
        f"• 🔥 Охота на Архонтов\n"
        f"• 🗡️ Стальной Путь\n"
        f"• 🚨 Тревоги\n"
        f"• 🌍 Циклы и погода (Земля, Дувири)\n"
        f"• 🛒 Торговцы\n"
        f"• 🌙 Ночная Волна\n\n"
        f"**📱 Виджет для смартфона:**\n"
        f"Перейди по ссылке для создания виджета:\n"
        f"`{create_widget_url(widget_token)}`"
    )
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        reply_markup=get_main_menu()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 **Помощь по боту**\n\n"
        "**Основные команды:**\n"
        "/start - Запустить бота\n"
        "/settings - Настройки уведомлений\n"
        "/info - Получить текущую информацию\n"
        "/widget - Получить ссылку на виджет\n"
        "/help - Показать эту справку\n\n"
        "**Типы уведомлений:**\n"
        "• Торговец из Бездны - прибытие и инвентарь\n"
        "• Разрывы Бездны - активные миссии\n"
        "• Вторжения - активные вторжения с наградами\n"
        "• Вылазка - ежедневное задание\n"
        "• Арбитраж - доступные миссии\n"
        "• Охота на Архонтов - еженедельное задание\n"
        "• Стальной Путь - ротационные награды\n"
        "• Тревоги - активные миссии\n"
        "• Циклы - смена дня/ночи, настроение Дувири\n"
        "• Торговцы - обновление инвентаря\n"
        "• Ночная Волна - сезонные награды"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = get_user(telegram_id)
    
    await update.message.reply_text(
        "⚙️ **Настройки уведомлений**\n\n"
        "Выбери категорию для настройки:",
        parse_mode='Markdown',
        reply_markup=get_settings_menu()
    )

async def widget_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = get_user(telegram_id)
    
    if not user.widget_token:
        widget_token = generate_widget_token(telegram_id)
    else:
        widget_token = user.widget_token
    
    widget_url = create_widget_url(widget_token)
    
    message = (
        "📱 **Виджет для смартфона**\n\n"
        "Создай виджет на рабочем столе для быстрого доступа к уведомлениям:\n\n"
        f"🔗 **Ссылка:**\n"
        f"`{widget_url}`\n\n"
        "**Как установить:**\n"
        "1. Скопируй ссылку\n"
        "2. На телефоне добавь виджет 'Web View' или 'URL'\n"
        "3. Вставь ссылку\n"
        "4. Настрой размер виджета"
    )
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 **Выбери информацию:**",
        parse_mode='Markdown',
        reply_markup=get_info_menu()
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    telegram_id = update.effective_user.id
    callback_data = query.data
    
    if callback_data == 'back_to_main':
        await query.edit_message_text(
            "👋 **Главное меню**\n\nВыбери действие:",
            parse_mode='Markdown',
            reply_markup=get_main_menu()
        )
        return
    
    elif callback_data == 'settings':
        await query.edit_message_text(
            "⚙️ **Настройки**\n\nВыбери категорию:",
            parse_mode='Markdown',
            reply_markup=get_settings_menu()
        )
        return
    
    elif callback_data == 'settings_main':
        user = get_user(telegram_id)
        await query.edit_message_text(
            "⚙️ **Основные настройки**\n\nВключи/выключи нужные уведомления:",
            parse_mode='Markdown',
            reply_markup=get_status_buttons(user.__dict__, 'main')
        )
        return
    
    elif callback_data == 'settings_cycles':
        user = get_user(telegram_id)
        await query.edit_message_text(
            "🌍 **Циклы и погода**\n\nНастрой уведомления о смене циклов:",
            parse_mode='Markdown',
            reply_markup=get_status_buttons(user.__dict__, 'cycles')
        )
        return
    
    elif callback_data == 'settings_traders':
        user = get_user(telegram_id)
        await query.edit_message_text(
            "🛒 **Торговцы**\n\nНастрой уведомления о торговцах:",
            parse_mode='Markdown',
            reply_markup=get_status_buttons(user.__dict__, 'traders')
        )
        return
    
    elif callback_data == 'get_info':
        await query.edit_message_text(
            "📊 **Выбери информацию:**",
            parse_mode='Markdown',
            reply_markup=get_info_menu()
        )
        return
    
    elif callback_data == 'info_cycles':
        await query.edit_message_text(
            "🌍 **Выбери цикл:**",
            parse_mode='Markdown',
            reply_markup=get_cycle_menu()
        )
        return
    
    elif callback_data == 'info_traders':
        await query.edit_message_text(
            "🛒 **Выбери торговца:**",
            parse_mode='Markdown',
            reply_markup=get_trader_menu()
        )
        return
    
    elif callback_data.startswith('toggle_'):
        setting_name = callback_data.replace('toggle_', '')
        user = get_user(telegram_id)
        
        current_value = getattr(user, setting_name, True)
        new_value = not current_value
        
        update_user_settings(telegram_id, **{setting_name: new_value})
        
        if setting_name.startswith('notify_'):
            if setting_name in ['notify_earth_cycle', 'notify_duviri_mood']:
                category = 'cycles'
            elif setting_name in ['notify_nightwave']:
                category = 'traders'
            else:
                category = 'main'
            
            user = get_user(telegram_id)
            status_text = "✅ Включено" if new_value else "❌ Выключено"
            
            await query.edit_message_text(
                f"⚙️ **Настройки**\n\nСтатус: {status_text}\n\nПродолжи настройку:",
                parse_mode='Markdown',
                reply_markup=get_status_buttons(user.__dict__, category)
            )
        return
    
    elif callback_data == 'widget':
        user = get_user(telegram_id)
        if not user.widget_token:
            widget_token = generate_widget_token(telegram_id)
        else:
            widget_token = user.widget_token
        
        widget_url = create_widget_url(widget_token)
        
        await query.edit_message_text(
            f"📱 **Виджет**\n\nСсылка: `{widget_url}`",
            parse_mode='Markdown',
            reply_markup=get_main_menu()
        )
        return
    
    elif callback_data == 'help':
        help_text = (
            "📖 **Помощь**\n\n"
            "Бот отправляет уведомления о событиях в Warframe.\n"
            "Настрой уведомления через меню настроек.\n\n"
            "Проект открыт на GitHub - можешь внести свой вклад!"
        )
        await query.edit_message_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=get_main_menu()
        )
        return
    
    elif callback_data.startswith('info_'):
        info_type = callback_data.replace('info_', '')
        
        await query.edit_message_text(
            "⏳ Получение информации...",
            reply_markup=get_main_menu()
        )
        
        data = None
        message = None
        
        try:
            if info_type == 'baro':
                data = await WarframeAPI.get_baro_trader()
                message = format_notification('baro', data)
            elif info_type == 'fissures':
                data = await WarframeAPI.get_fissures()
                message = format_notification('fissures', data)
            elif info_type == 'invasions':
                data = await WarframeAPI.get_invasions()
                message = format_notification('invasions', data)
            elif info_type == 'sortie':
                data = await WarframeAPI.get_sortie()
                message = format_notification('sortie', data)
            elif info_type == 'arbitration':
                data = await WarframeAPI.get_arbitration()
                message = format_notification('arbitration', data)
            elif info_type == 'archon':
                data = await WarframeAPI.get_archon_hunt()
                message = format_notification('archon', data)
            elif info_type == 'steel_path':
                data = await WarframeAPI.get_steel_path()
                message = format_notification('steel_path', data)
            elif info_type == 'alerts':
                data = await WarframeAPI.get_alerts()
                message = format_notification('alerts', data)
            elif info_type == 'earth_cycle':
                data = await WarframeAPI.get_earth_cycle()
                if data:
                    message = format_notification('earth_cycle', data)
                else:
                    message = "🌍 Данные о цикле Земли недоступны"
            elif info_type == 'duviri_mood':
                data = await WarframeAPI.get_duviri_mood()
                if data:
                    message = format_notification('duviri_mood', data)
                else:
                    message = "🎭 Данные о настроении Дувири недоступны"
            elif info_type == 'nightwave':
                data = await WarframeAPI.get_nightwave()
                if data:
                    message = format_notification('nightwave', data)
                else:
                    message = "🌙 Ночная Волна сейчас недоступна"
            elif info_type == 'all':
                tasks = [
                    WarframeAPI.get_baro_trader(),
                    WarframeAPI.get_fissures(),
                    WarframeAPI.get_invasions(),
                    WarframeAPI.get_sortie(),
                    WarframeAPI.get_arbitration(),
                    WarframeAPI.get_archon_hunt(),
                    WarframeAPI.get_steel_path(),
                    WarframeAPI.get_alerts(),
                    WarframeAPI.get_earth_cycle(),
                    WarframeAPI.get_duviri_mood(),
                    WarframeAPI.get_nightwave()
                ]
                
                results = await asyncio.gather(*tasks)
                
                message = "📊 **Вся информация:**\n\n"
                
                data_map = [
                    ('🧛 Торговец из Бездны', 'baro', results[0]),
                    ('💠 Разрывы Бездны', 'fissures', results[1]),
                    ('⚔️ Вторжения', 'invasions', results[2]),
                    ('🎯 Вылазка', 'sortie', results[3]),
                    ('⚡ Арбитраж', 'arbitration', results[4]),
                    ('🔥 Охота на Архонтов', 'archon', results[5]),
                    ('🗡️ Стальной Путь', 'steel_path', results[6]),
                    ('🚨 Тревоги', 'alerts', results[7]),
                    ('🌍 Цикл Земли', 'earth_cycle', results[8]),
                    ('🎭 Настроение Дувири', 'duviri_mood', results[9]),
                    ('🌙 Ночная Волна', 'nightwave', results[10])
                ]
                
                for name, data_type, result in data_map:
                    message += f"=== {name} ===\n"
                    if result:
                        message += format_notification(data_type, result)
                    else:
                        message += "Нет данных\n"
                    message += "\n\n"
            
            if message:
                await query.message.reply_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=get_info_menu()
                )
            else:
                await query.message.reply_text(
                    "❌ Не удалось получить информацию",
                    reply_markup=get_info_menu()
                )
        except Exception as e:
            print(f"Error in button_callback: {e}")
            await query.message.reply_text(
                f"❌ Ошибка получения данных: {str(e)}",
                reply_markup=get_info_menu()
            )
        return

async def send_notification(context: ContextTypes.DEFAULT_TYPE, telegram_id: int, message: str, notification_type: str):
    try:
        await context.bot.send_message(
            chat_id=telegram_id,
            text=message,
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Error sending notification to {telegram_id}: {e}")
