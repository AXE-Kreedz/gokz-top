import asyncio
import logging
import sys

from tqdm import tqdm

from app.core.database.records import get_latest_record_id, insert_records

from app import logger
from app.core.globalapi.globalapi import get_record


async def update_records(end_id=24329598):
    start_id = await get_latest_record_id()
    with tqdm(total=end_id - start_id, colour='green', ncols=100, desc=f'Updating records {start_id}:') as pbar:
        for record_id in range(start_id, end_id):
            data = await get_record(record_id)
            await insert_records(data)
            pbar.set_description(f"Updating Record ID: {record_id}")
            pbar.update(1)


async def main():
    await update_records()

if __name__ == '__main__':
    logger.setLevel('DEBUG')

    task = update_records()
    asyncio.run(task)
