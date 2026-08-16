🎯 Pocket Cephalon - Warframe Notification Bot
<div align="center">
https://img.shields.io/badge/Pocket_Cephalon-Warframe_Bot-blue?style=for-the-badge&logo=telegram
https://img.shields.io/badge/version-2.0.0-green?style=flat-square
https://img.shields.io/badge/Python-3.10+-yellow?style=flat-square&logo=python
https://img.shields.io/badge/Telegram-Bot-blue?style=flat-square&logo=telegram
https://img.shields.io/badge/Railway-Deployed-success?style=flat-square&logo=railway

https://img.shields.io/badge/%F0%9F%A4%96_Try_Bot-@Pocketcephalonbot-blue?style=for-the-badge&logo=telegram
https://img.shields.io/badge/%F0%9F%93%B1_Widget-Available-brightgreen?style=for-the-badge

</div>
Pocket Cephalon - это мощный Telegram бот для отслеживания событий в игре Warframe. Получайте мгновенные уведомления о всех важных событиях, настраивайте уведомления под себя и используйте удобный виджет для смартфона!

✨ Возможности бота
📊 Основные уведомления
Событие	Описание	Эмодзи
Торговец из Бездны	Прибытие Baro Ki'Teer с полным инвентарем и ценами	🧛
Разрывы Бездны	Все активные разрывы с типами миссий и врагами	💠
Вторжения	Активные вторжения с наградами (Реакторы/Катализаторы)	⚔️
Сортировка	Ежедневное задание с боссами и наградами	🎯
Арбитраж	Тип миссии, тир карты, враги, рекомендации	⚡
Охота на Архонтов	Еженедельные миссии с боссами	🔥
Стальной Путь	Ротационные награды и информер	🗡️
Тревоги	Все активные тревоги с наградами	🚨
🌍 Циклы и погода
Земля - Смена дня и ночи 🌍

Венера - Погодные условия (тепло/холодно) 🌡️

Деймос - Циклы Фасс/Воме 🕷️

Дувири - Настроение (Радость/Зависть/Страх/Гнев/Печаль) 🎭

🛒 Торговцы
Эрго Гласт - Инвентарь с характеристиками оружия

Элеонора - Инвентарь с характеристиками оружия

⚡ Специальные уведомления
🚀 Реакторы Орокин - Мгновенные уведомления о появлении

🔧 Катализаторы Орокин - Мгновенные уведомления о появлении

📱 Виджет для смартфона
<div align="center"> <img src="https://i.imgur.com/example-widget.png" alt="Widget Preview" width="300"> </div>
Особенности виджета:

📱 Показывает последние 20 уведомлений

🔄 Автообновление каждые 60 секунд

🎨 Стильный темный дизайн

📊 Быстрый доступ к информации

🔗 Прямая ссылка на бота

Получить виджет →

🎮 Команды бота
Команда	Описание
/start	Запуск бота и регистрация
/settings	Настройка уведомлений
/info	Получение текущей информации
/widget	Получить ссылку на виджет
/help	Помощь и справка
🎯 Примеры уведомлений
Торговец из Бездны
text
🧛 Baro Ki'Teer
📍 Местоположение: Реле Орбитер
⏰ Доступен до: 2026-08-20 14:00

🛍️ Инвентарь:
• Прайм Мод - 100🪙 200000💰
• Прайм Оружие - 50🪙 100000💰
Арбитраж
text
⚡ Арбитраж

📍 Узел: Мот, Войд
🎯 Тип миссии: Выживание
👾 Враг: Корпус
⭐ Тир карты: Элитный
⏰ Доступен до: 2026-08-20 16:00

💡 Рекомендуется: Танк/Поддержка
🛠️ Технические детали
Стек технологий
Python 3.10+ - Основной язык

python-telegram-bot - Библиотека для Telegram API

SQLAlchemy - ORM для работы с БД

APScheduler - Планировщик задач

FastAPI - Веб-сервер для виджета

SQLite/PostgreSQL - База данных

Архитектура
text
├── bot.py              # Основной файл бота
├── handlers.py         # Обработчики команд
├── warframe_api.py     # API клиент для Warframe
├── scheduler.py        # Планировщик уведомлений
├── database.py         # Модели и работа с БД
├── keyboards.py        # Клавиатуры и меню
├── widget/            # Веб-виджет
│   ├── index.html
│   ├── widget.css
│   └── widget.js
└── web/               # Веб-сервер
    └── server.py
Особенности реализации
⚡ Мгновенные уведомления - Проверка событий каждые 30 секунд

🛡️ Защита от блокировки - Rate limit 5 секунд между сообщениями

📨 Очередь уведомлений - Ни одно уведомление не потеряется

💾 История - Все уведомления сохраняются в БД

🎯 Гибкая настройка - Каждый тип уведомления включается отдельно

🚀 Развертывание
На Railway (рекомендуется)
Форкните репозиторий

Создайте проект на Railway

Подключите GitHub репозиторий

Добавьте переменные окружения:

env
BOT_TOKEN=ваш_токен_бота
DATABASE_URL=postgresql://...
WEB_PORT=8000
RATE_LIMIT=5
Нажмите "Deploy"

Локальный запуск
bash
# Клонирование репозитория
git clone https://github.com/your-username/warframe-bot.git
cd warframe-bot

# Установка зависимостей
pip install -r requirements.txt

# Настройка .env файла
cp .env.example .env
# Отредактируйте .env с вашими данными

# Запуск бота
python bot.py
Переменные окружения
Переменная	Описание	По умолчанию
BOT_TOKEN	Токен Telegram бота	Обязательно
DATABASE_URL	URL базы данных	sqlite:///warframe_bot.db
WEB_PORT	Порт веб-сервера	8000
RATE_LIMIT	Секунд между сообщениями	5
API_KEY	Ключ Warframe API (опционально)	-
📊 Статистика
<div align="center">
https://img.shields.io/badge/Users-500+-blue?style=flat-square
https://img.shields.io/badge/Notifications-10K+-green?style=flat-square
https://img.shields.io/badge/Uptime-99.9%2525-brightgreen?style=flat-square

</div>
🤝 Вклад в проект
Мы приветствуем любые contributions!

Как помочь:
🐛 Сообщайте об ошибках - Создайте Issue

💡 Предлагайте идеи - Новые функции и улучшения

🔧 Исправляйте баги - Отправляйте Pull Request

📝 Улучшайте документацию - Исправляйте опечатки и неточности

🌍 Переводы - Помогите перевести бота на другие языки

Разработка
bash
# Установка зависимостей для разработки
pip install -r requirements-dev.txt

# Запуск тестов
pytest

# Проверка стиля кода
flake8 .
black .
📝 Лицензия
MIT License - подробнее в файле LICENSE

🙏 Благодарности
Warframe API - За отличное API

python-telegram-bot - За мощную библиотеку

Все пользователи бота - За вашу поддержку и обратную связь

📞 Контакты
Бот: @Pocketcephalonbot

<div align="center">
⭐ Не забудьте поставить звезду репозиторию!

Попробовать бота →

</div>
📸 Скриншоты
<div align="center">
Главное меню	Настройки	Уведомление
https://i.imgur.com/menu.png	https://i.imgur.com/settings.png	https://i.imgur.com/notification.png
</div>
