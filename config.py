import json
import csv
import os
from dotenv import load_dotenv

load_dotenv()

script_dir = os.path.dirname(os.path.realpath(__file__))
map_tiers_path = os.path.join(script_dir, 'jsons/map_tiers.json')
vnl_tiers_path = os.path.join(script_dir, 'jsons/vnl_tiers.csv')


with open(map_tiers_path, 'r') as f:
    MAP_TIERS: dict = json.load(f)

with open(vnl_tiers_path, 'r') as f:
    VNL_TIERS: dict = {row['Name']: row['TP Tier'] for row in csv.DictReader(f)}

DB2_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    'db': os.getenv("DB_DB"),
}

STEAM_API_KEY = os.getenv("STEAM_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
