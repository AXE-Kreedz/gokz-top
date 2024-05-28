from app import logger
from app.core.database.leaderboard import update_player_rank
from app.core.database.records import fetch_pb_records, filter_pb_records
from app.core.globalapi import TooManyRequestsException
from app.core.globalapi.globalapi import get_personal_all_records
from app.core.skill_points.skill_points import calc_skill_pts
from app.core.utils.steam_user import get_steam_user_info


async def update_player_skill_pts(steamid: str | int, mode='kz_timer', from_local=False, update_steam_info=True):
    if from_local:
        records = await fetch_pb_records(steamid, mode)
    else:
        try:
            records = await get_personal_all_records(steamid, mode, True)
        except TooManyRequestsException as e:
            logger.warning(f"Too Many Requests! {steamid} {repr(e)}")
            return False
        records = filter_pb_records(records)

    if not records:
        logger.debug(f"No records found for {steamid}")
        return None

    player_data = calc_skill_pts(records)

    if update_steam_info:
        steam_info = await get_steam_user_info(player_data['steamid'])
        if steam_info:
            player_data['name'] = steam_info['personaname']
            player_data['avatar_hash'] = steam_info['avatarhash']
    await update_player_rank(player_data, mode=mode)
    return True
