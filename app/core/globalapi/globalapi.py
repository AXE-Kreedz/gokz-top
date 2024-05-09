import asyncio
import json
import logging
import time
from json import JSONDecodeError

from aiohttp import ClientSession

from app.core.utils.steam_user import conv_steamid
from app import logger

URL = "https://kztimerglobal.com/api/v2.0/"


async def get_record(record_id: int) -> dict | None:
    url = f"{URL}records/{record_id}"

    async with ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.text()
            if data == 'null':
                return None

            try:
                data = json.loads(data)
                return data
            except json.JSONDecodeError as e:
                logger.warning(f"record: {record_id} {repr(e)} {data}")
                raise Exception(f"Too Many Requests! {record_id} {repr(e)} {data}")


async def get_personal_global_records(steamid, mode_str="kz_timer", has_tp=True, stage=0) -> list | None:
    steamid64 = conv_steamid(steamid, 64)

    url = (
        f"{URL}records/top?&steamid64={steamid64}&tickrate=128&stage={stage}"
        f"&modes_list_string={mode_str}&limit=10000&has_teleports={has_tp}"
    )

    async with ClientSession() as session:
        try:
            async with session.get(url, ssl=False) as response:
                try:
                    data = await response.json(content_type=None)
                    return data
                except JSONDecodeError:
                    logging.error(f"Failed to get personal global records for {steamid} in {mode_str} mode", await response.text())
                    return None
        except Exception as e:
            logging.error(f"Failed to get personal global records for {steamid} in {mode_str} mode", e)
            return None


async def get_personal_all_records(steamid, mode=None) -> list:
    tasks = []

    if mode:
        tasks.append(get_personal_global_records(steamid, mode, True))
        tasks.append(get_personal_global_records(steamid, mode, False))
    else:
        tasks.extend([
            get_personal_global_records(steamid, "kz_timer", True),
            get_personal_global_records(steamid, "kz_timer", False),
            get_personal_global_records(steamid, "kz_simple", True),
            get_personal_global_records(steamid, "kz_simple", False),
            get_personal_global_records(steamid, "kz_vanilla", True),
            get_personal_global_records(steamid, "kz_vanilla", False),
        ])
    results = await asyncio.gather(*tasks)
    records = [record for result in results if result is not None for record in result]
    return records
