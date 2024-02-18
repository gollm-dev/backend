import os
from dotenv import load_dotenv

# Loading env variables from .env file
load_dotenv('.env')

MONGO_URI = os.getenv('MONGO_URI')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_LOGS_CHANNEL = os.getenv('TELEGRAM_LOGS_CHANNEL')
