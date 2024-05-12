import asyncio
import time
import sys

from tqdm import tqdm
from datetime import datetime, timedelta

from app.core.database.records import get_latest_record_id, insert_records

from app import logger
from app.core.globalapi.globalapi import get_record, personal_best


async def update_records(end_id=30_000_000):
    start_id = await get_latest_record_id()
    with tqdm(total=end_id - start_id, colour='blue', desc=f'Updating Records: {start_id}:') as pbar:
        for record_id in range(start_id, end_id):
            data = None
            while data is None:
                try:
                    data = await get_record(record_id)
                    while not data:
                        data = await get_record(record_id)
                        pbar.set_postfix({'last': datetime.now().strftime('%H:%M:%S')})
                        time.sleep(60)
                except Exception as e:
                    logger.warning(e)
                    pbar.set_postfix({'last': datetime.now().strftime('%H:%M:%S')})
                    time.sleep(300)
            while True:
                pb = await personal_best(data['steamid64'], data['map_id'], data['mode'], True if data['teleports'] else False)
                if pb:
                    break
                pbar.set_postfix({'last': datetime.now().strftime('%H:%M:%S')})
                time.sleep(60)
            if pb.get('id') == data['id']:
                data['points'] = pb['points']
            await insert_records(data)

            dt = datetime.fromisoformat(data['created_on'])
            dt = dt + timedelta(hours=8)
            pbar.set_description(
                f"Updating {record_id:,} - {data['points']}pts - {dt.strftime('%H:%M:%S')}"
            )
            pbar.update(1)


async def main():
    await update_records()

if __name__ == '__main__':
    logger.setLevel('INFO')

    task = update_records()
    try:
        asyncio.run(task)
    except KeyboardInterrupt:
        print('Exiting...')
        time.sleep(1)
        sys.exit(0)
