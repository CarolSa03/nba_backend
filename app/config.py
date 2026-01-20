import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_KEY = os.environ.get('API_KEY')
    BASE_URL = 'https://api.balldontlie.io/v1'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.environ.get('PORT', 10000))

    # Debug
    @classmethod
    def init_app(cls):
        print(f"API_KEY loaded: {cls.API_KEY[:10] if cls.API_KEY else 'None'}...")
