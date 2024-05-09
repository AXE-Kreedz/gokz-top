import asyncio
import json
import time

from tqdm import tqdm
from datetime import datetime

from app import logger
from app.core.database.records import get_players_steamids
from app.core.globalapi.globalapi import get_personal_all_records


async def update_personal_records(steamids):
    with tqdm(steamids, colour='blue', ncols=100) as pbar:
        for steamid in steamids:
            pbar.set_description(f"Updating {steamid} ")

            data = None
            while data is None:
                try:
                    data = await get_personal_all_records(steamid, 'kz_timer')

                except Exception as e:
                    logger.warning(e)
                    pbar.set_postfix({'last': datetime.now().strftime('%H:%M:%S')})
                    pbar.set_description(f"Updating {steamid} - Too Many Requests, waiting...", refresh=True)
                    time.sleep(300)

            with open(f'jsons/kzt/{steamid}.json', 'w') as f:
                json.dump(data, f)

            pbar.update(1)


async def main():
    with open('jsons/players_steamids.json', 'r') as f:
        steamids = json.load(f)
    await update_personal_records(steamids)


if __name__ == '__main__':
    logger.setLevel('INFO')

    task = main()
    try:
        asyncio.run(task)
    except KeyboardInterrupt:
        print('Exiting...')
        time.sleep(1)
        exit(0)
