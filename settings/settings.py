import json
from os import getenv
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / 'config' / '.env'
abi_path = Path(__file__).parent.parent / 'config' / 'abi.json'

load_dotenv(dotenv_path=env_path)

# bot settings
BOT_TOKEN = getenv('BOT_TOKEN')

# contract settings
with abi_path.open() as abi_file:
    CONTRACT_ABI = json.load(abi_file)

PROVIDER_URL = getenv('PROVIDER_URL')
CONTRACT_ADDRESS = getenv('CONTRACT_ADDRESS')
START_BLOCK = getenv('START_BLOCK')
TOKEN_ID = getenv('TOKEN_ID')

# db settings
DB_NAME = getenv('DB_NAME')
DB_USERNAME = getenv('DB_USERNAME')
DB_PASSWORD = getenv('DB_PASSWORD')
