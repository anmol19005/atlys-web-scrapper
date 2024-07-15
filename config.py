import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv('DATABASE_URL')
    API_TOKEN = os.getenv('API_TOKEN')
    WEBSITE_URL = os.getenv('WEBSITE_URL')
    REDIS_URL = os.getenv('REDIS_URL')
