import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///warframe_bot.db')
WEB_PORT = int(os.getenv('WEB_PORT', 8000))
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
RATE_LIMIT = int(os.getenv('RATE_LIMIT', 5))
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 30))
API_KEY = os.getenv('API_KEY')

# Warframe API URL
WARFRAME_API_URL = "https://api.warframestat.us/pc"