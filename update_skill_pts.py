import argparse
import asyncio
import json
import time

from tqdm import tqdm

from app import logger
from app.core.database.leaderboard import update_player_rank
from app.core.database.records import fetch_pb_records, filter_pb_records
from app.core.globalapi.globalapi import get_personal_all_records
from app.core.skill_points.skill_points import calc_skill_pts


async def updating_players_rank(steamids: list, from_local=True, update_steam_info=True):
    for steamid in tqdm(steamids, desc='Updating Players Ranks', colour='blue', unit='player', ncols=100):
        if from_local:
            records = await fetch_pb_records(steamid)
        else:
            records = await get_personal_all_records(steamid, 'kz_timer', True)
            records = filter_pb_records(records)

        if not records:
            logger.debug(f"No records found for {steamid}")
            continue

        player_data = calc_skill_pts(records)
        await update_player_rank(player_data, update_steam_info=update_steam_info)


# Finished: 1, 9
async def main(part):
    logger.info(f"Updating skill points for part {part}")
    with open(f'jsons/steamids_{part}.json', 'r') as f:
        steamids = json.load(f)
    await updating_players_rank(steamids, from_local=True, update_steam_info=True)


if __name__ == '__main__':
    logger.setLevel('INFO')

    parser = argparse.ArgumentParser(description="Update Player Skill Points")
    parser.add_argument('part', type=int, help='An integer for the accumulator(0-9)')
    args = parser.parse_args()

    try:
        asyncio.run(main(args.part))
    except KeyboardInterrupt:
        logger.warning('Exiting...')
        time.sleep(1)
        exit(0)
