import json
import os

from dotenv import load_dotenv

load_dotenv()

with open('jsons/map_tiers.json', 'r') as f:
    MAP_TIERS = json.load(f)

DB2_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    'db': os.getenv("DB_DB"),
}

STEAM_API_KEY = os.getenv("STEAM_API_KEY")
