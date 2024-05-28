import argparse
import asyncio
import json
import time

from tqdm import tqdm

from app import logger
from app.core.skill_points.update import update_player_skill_pts


async def updating_players_rank(steamids: list, mode, from_local=True, update_steam_info=True, step=2):
    progress_bar = tqdm(total=len(steamids), desc='Updating Players Ranks', colour='blue', unit='player', ncols=100)
    for i in range(0, len(steamids), step):
        progress_bar.set_description(f"Updating Players Ranks {i + 1}/{len(steamids)}")
        batch = steamids[i:i + step]
        await asyncio.gather(*(update_player_skill_pts(steamid, mode, from_local, update_steam_info) for steamid in batch))
        progress_bar.update(len(batch))
    progress_bar.close()


async def main(part, num=None):
    logger.info(f"Updating skill points for part {part}")
    with open(f'jsons/steamids_vnl.json', 'r') as f:
        steamids = json.load(f)

    steamids = steamids

    # with open('jsons/steamids_vnl.json', 'r') as f:
    #     steamids = json.load(f)
    await updating_players_rank(steamids, mode='kz_vanilla', from_local=True, update_steam_info=False, step=4)


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
