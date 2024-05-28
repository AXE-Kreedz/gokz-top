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
                    data = await get_personal_all_records(steamid, 'kz_vanilla')
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


async def main(part=0, reverse=False):
    with open(f'jsons/steamids_skz_1.json', 'r') as f:
        steamids = list(set(json.load(f)))
    # if reverse:
    #     steamids = steamids[::-1]
    if part == 0:
        steamids = steamids[:len(steamids) // 2][::-1]
    elif part == 1:
        steamids = steamids[len(steamids) // 2:]
    await update_personal_records(steamids)


if __name__ == '__main__':
    logger.setLevel('INFO')

    parser = argparse.ArgumentParser(description="Update player records")
    parser.add_argument('part', type=int, help='An integer for the accumulator(0-9)')
    parser.add_argument('--reverse', action='store_true', help='Reverse the order of the steamids')

    args = parser.parse_args()

    try:
        asyncio.run(main(args.part, args.reverse))
    except KeyboardInterrupt:
        logger.warning('Exiting...')
        time.sleep(1)
        exit(0)
