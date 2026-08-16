// Получаем токен из URL
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');

if (!token) {
    document.getElementById('notifications').innerHTML = `
        <div class="loading">❌ Токен не найден</div>
    `;
}

// Конфигурация
const API_URL = 'https://ваш-railway-url.railway.app/api/widget';
const TELEGRAM_BOT_URL = 'https://t.me/ваш_бот_username';

// Загрузка данных
async function loadData() {
    try {
        const response = await fetch(`${API_URL}?token=${token}`);
        const data = await response.json();
        
        if (data.success) {
            displayNotifications(data.notifications);
            updateTime(data.timestamp);
        } else {
            showError(data.error || 'Ошибка загрузки');
        }
    } catch (error) {
        console.error('Error loading data:', error);
        showError('Ошибка соединения');
    }
}

// Отображение уведомлений
function displayNotifications(notifications) {
    const container = document.getElementById('notifications');
    
    if (!notifications || notifications.length === 0) {
        container.innerHTML = `
            <div class="loading">📭 Нет новых уведомлений</div>
        `;
        return;
    }
    
    let html = '';
    notifications.forEach(notif => {
        const typeClass = notif.type || 'default';
        const content = notif.content.replace(/\n/g, '<br>');
        const time = new Date(notif.timestamp).toLocaleTimeString();
        
        html += `
            <div class="notification-item ${typeClass}">
                <div class="type">${getTypeName(notif.type)}</div>
                <div class="content">${content}</div>
                <div class="time">${time}</div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Получение названия типа
function getTypeName(type) {
    const types = {
        'baro': '🧛 Торговец',
        'fissures': '💠 Разрывы',
        'invasions': '⚔️ Вторжения',
        'sortie': '🎯 Сортировка',
        'arbitration': '⚡ Арбитраж',
        'archon': '🔥 Архонты',
        'steel_path': '🗡️ Стальной путь',
        'alerts': '🚨 Тревоги',
        'earth_cycle': '🌍 Земля',
        'venus_weather': '🌡️ Венера',
        'deimos_cycle': '🕷️ Деймос',
        'duviri_mood': '🎭 Дувири',
        'ergo_glast': '🛒 Эрго Гласт',
        'eleonora': '🛒 Элеонора',
        'special_reactor': '⚡ Реактор',
        'special_catalyst': '🔧 Катализатор'
    };
    return types[type] || type || 'Уведомление';
}

// Обновление времени
function updateTime(timestamp) {
    const timeElement = document.getElementById('updateTime');
    const date = new Date(timestamp);
    timeElement.textContent = `Обновлено: ${date.toLocaleTimeString()}`;
}

// Показ ошибки
function showError(message) {
    const container = document.getElementById('notifications');
    container.innerHTML = `
        <div class="loading">❌ ${message}</div>
    `;
}

// Обновление данных
function refreshData() {
    const button = document.querySelector('.footer button:first-child');
    button.textContent = '⏳ Загрузка...';
    button.disabled = true;
    
    loadData().finally(() => {
        button.textContent = '🔄 Обновить';
        button.disabled = false;
    });
}

// Открытие бота в Telegram
function openTelegram() {
    window.open(TELEGRAM_BOT_URL, '_blank');
}

// Автообновление каждые 60 секунд
setInterval(loadData, 60000);

// Загрузка при старте
loadData();

// Service Worker для офлайн-режима
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
        .then(registration => {
            console.log('ServiceWorker registered');
        })
        .catch(err => {
            console.log('ServiceWorker registration failed:', err);
        });
}