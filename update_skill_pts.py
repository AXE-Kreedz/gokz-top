import argparse
import asyncio
import json
import time

from tqdm import tqdm

from app import logger
from app.core.skill_points.update import update_player_skill_pts


async def updating_players_rank(steamids: list, from_local=True, update_steam_info=True, step=2):
    progress_bar = tqdm(total=len(steamids), desc='Updating Players Ranks', colour='blue', unit='player', ncols=100)
    for i in range(0, len(steamids), step):
        progress_bar.set_description(f"Updating Players Ranks {i + 1}/{len(steamids)}")
        batch = steamids[i:i + step]
        await asyncio.gather(*(update_player_skill_pts(steamid, 'kz_timer', from_local, update_steam_info) for steamid in batch))
        progress_bar.update(len(batch))
    progress_bar.close()


# Finished: 1, 9, 0, 8, 2 [ 3, 4, 5, 6, 7
async def main(part, num=None):
    logger.info(f"Updating skill points for part {part}")
    with open(f'jsons/steamids_{part}.json', 'r') as f:
        steamids = json.load(f)
    if num:
        steamids = steamids[:num]
    await updating_players_rank(steamids, from_local=True, update_steam_info=True)


if __name__ == '__main__':
    logger.setLevel('WARNING')
    parser = argparse.ArgumentParser(description="Update Player Skill Points")
    parser.add_argument('part', type=int)
    parser.add_argument('--num', type=int, default=None)
    args = parser.parse_args()
    try:
        asyncio.run(main(args.part, args.num))
    except KeyboardInterrupt:
        logger.warning('Exiting...')
        time.sleep(1)
        exit(0)
