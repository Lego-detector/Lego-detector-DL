import os
from dotenv import load_dotenv

load_dotenv(override=True)

class ENV():
    _instance = None

    DEBUG_MODE = os.getenv('DEBUG_MODE')
    MQ_HOST = os.getenv('MQ_HOST')
    MQ_PORT = os.getenv('MQ_PORT')
    MQ_USER = os.getenv('MQ_USER')
    MQ_PWD = os.getenv('MQ_PWD')