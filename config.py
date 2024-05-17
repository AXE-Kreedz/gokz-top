import json
import os
from dotenv import load_dotenv

load_dotenv()

script_dir = os.path.dirname(os.path.realpath(__file__))
map_tiers_path = os.path.join(script_dir, 'jsons/map_tiers.json')


with open(map_tiers_path, 'r') as f:
    MAP_TIERS: dict = json.load(f)

DB2_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    'db': os.getenv("DB_DB"),
}

STEAM_API_KEY = os.getenv("STEAM_API_KEY")
