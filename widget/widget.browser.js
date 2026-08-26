// Проверяем, что мы в браузере, а не в Node.js
if (typeof window !== 'undefined') {
    
    // Получаем токен из URL
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    // Проверка наличия токена
    const notificationsContainer = document.getElementById('notifications');
    if (!token) {
        if (notificationsContainer) {
            notificationsContainer.innerHTML = `
                <div class="loading">❌ Токен не найден</div>
            `;
        }
    }
    
    // Конфигурация - используем относительный путь
    const API_URL = '/api/widget';
    const TELEGRAM_BOT_URL = 'https://t.me/Pocketcephalonbot'; // Замените на ваш username
    
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
        
        if (!container) return;
        
        if (!notifications || notifications.length === 0) {
            container.innerHTML = `
                <div class="loading">📭 Нет новых уведомлений</div>
            `;
            return;
        }
        
        let html = '';
        notifications.forEach(notif => {
            const typeClass = notif.type || 'default';
            const content = (notif.content || '').replace(/\n/g, '<br>');
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
            'sortie': '🎯 Вылазка',
            'arbitration': '⚡ Арбитраж',
            'archon': '🔥 Архонты',
            'steel_path': '🗡️ Стальной путь',
            'alerts': '🚨 Тревоги',
            'earth_cycle': '🌍 Земля',
            'venus_weather': '🌡️ Венера',
            'deimos_cycle': '🕷️ Деймос',
            'duviri_mood': '🎭 Дувири',
            'nightwave': '🌙 Ночная Волна'
        };
        return types[type] || type || 'Уведомление';
    }
    
    // Обновление времени
    function updateTime(timestamp) {
        const timeElement = document.getElementById('updateTime');
        if (timeElement) {
            const date = new Date(timestamp);
            timeElement.textContent = `Обновлено: ${date.toLocaleTimeString()}`;
        }
    }
    
    // Показ ошибки
    function showError(message) {
        const container = document.getElementById('notifications');
        if (container) {
            container.innerHTML = `
                <div class="loading">❌ ${message}</div>
            `;
        }
    }
    
    // Обновление данных
    function refreshData() {
        const button = document.querySelector('.footer button:first-child');
        if (button) {
            button.textContent = '⏳ Загрузка...';
            button.disabled = true;
            
            loadData().finally(() => {
                button.textContent = '🔄 Обновить';
                button.disabled = false;
            });
        }
    }
    
    // Открытие бота в Telegram
    function openTelegram() {
        window.open(TELEGRAM_BOT_URL, '_blank');
    }
    
    // Делаем функции доступными глобально для HTML-кнопок
    window.refreshData = refreshData;
    window.openTelegram = openTelegram;
    
    // Загрузка при старте
    loadData();
    
    // Автообновление каждые 60 секунд
    setInterval(loadData, 60000);
    
    // Service Worker для офлайн-режима (опционально)
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('ServiceWorker registered');
            })
            .catch(err => {
                console.log('ServiceWorker registration failed:', err);
            });
    }
    
} else {
    // Если скрипт запущен в Node.js - ничего не делаем
    console.log('Widget.js is running in Node.js environment - skipping browser-specific code');
}
