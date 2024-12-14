import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get('TOKEN')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
DB_PATH = os.environ.get('DB_PATH')

