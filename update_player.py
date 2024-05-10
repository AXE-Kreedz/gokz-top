import asyncio
import json
import os
import time
import argparse

from tqdm import tqdm
from datetime import datetime

from app import logger
from app.core.database.records import update_points
from app.core.globalapi import TooManyRequestsException
from app.core.globalapi.globalapi import get_personal_all_records


async def update_personal_records(steamids, cache=True):
    if not isinstance(steamids, list):
        steamids = [steamids]
    processed_steamids = set()
    processed_file = 'jsons/processed_steamids.json'
    if cache:
        if os.path.exists(processed_file):
            with open(processed_file, 'r') as f:
                processed_steamids = set(json.load(f))
                steamids = [steamid for steamid in steamids if steamid not in processed_steamids]
    with tqdm(steamids, colour='blue', ncols=100) as pbar:
        for steamid in steamids:
            pbar.set_description(f"Updating {steamid} ")
            data = None
            while data is None:
                try:
                    data = await get_personal_all_records(steamid)
                except TooManyRequestsException as e:
                    pbar.set_postfix({'last': datetime.now().strftime('%H:%M:%S')})
                    pbar.set_description(f"Updating {steamid} {e}", refresh=True)
                    time.sleep(120)

            await update_points(data)
            pbar.set_description(f"Updating {steamid} - Done")
            pbar.update(1)

            if cache:
                processed_steamids.add(steamid)
                with open(processed_file, 'w') as f:
                    json.dump(list(processed_steamids), f)


async def main(part=0):
    with open(f'jsons/steamids_{part}.json', 'r') as f:
        steamids = json.load(f)
    await update_personal_records(steamids)


if __name__ == '__main__':
    logger.setLevel('INFO')

    parser = argparse.ArgumentParser(description="Update player records")
    parser.add_argument('part', type=int, help='An integer for the accumulator(0-9)')
    args = parser.parse_args()

    try:
        asyncio.run(main(args.part))
    except KeyboardInterrupt:
        logger.warning('Exiting...')
        time.sleep(1)
        exit(0)
