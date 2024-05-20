import asyncio
import sys

from tqdm import tqdm

from app.core.database.leaderboard import get_steamids_with_empty_avatar, update_avatar_hash
from app.core.utils.steam_user import get_steam_user_info
from app import logger


async def main():
    steamids = await get_steamids_with_empty_avatar()
    for steamid in tqdm(steamids, colour='blue', ncols=100):
        info = await get_steam_user_info(steamid)
        if info:
            await update_avatar_hash(steamid, info['avatarhash'])


if __name__ == '__main__':
    logger.setLevel('INFO')
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exiting...')
        sys.exit(0)
