from pathlib import Path
from dotenv import load_dotenv
from os import environ
from uuid import uuid4

DEBUG = True

if Path('.env').exists():
    load_dotenv()

class Config:
    APP_NAME = environ.get('APP_NAME', 'fahnder')
    CONFLUENCE_ACCESS_TOKEN = environ.get('CONFLUENCE_ACCESS_TOKEN')
    JIRA_ACCESS_TOKEN = environ.get('JIRA_ACCESS_TOKEN')
    CONFIG_FILE = environ.get('CONFIG_FILE', 'fahnder.yml')
    DEBUG = environ.get('DEBUG')
    TESTING = environ.get('TESTING')
    FRONTEND_URL = environ.get('FRONTEND_URL', "")
    SECRET_KEY = uuid4().hex
    auths = {}

def is_true(env_value):
    if not env_value:
        return False

    if env_value is True:
        return True

    return env_value.lower() in ("1", "yes", "true", "on")
