import os
from dotenv import load_dotenv

load_dotenv()

class ENV():
    _instance = None

    DEBUG_MODE = os.getenv("DEBUG_MODE")
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")
    REDIS_USER = os.getenv("REDIS_USER")
    REDIS_PWD = os.getenv("REDIS_PWD")