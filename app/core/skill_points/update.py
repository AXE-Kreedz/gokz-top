from app import logger
from app.core.database.leaderboard import update_player_rank
from app.core.database.records import fetch_pb_records, filter_pb_records
from app.core.globalapi.globalapi import get_personal_all_records
from app.core.skill_points.skill_points import calc_skill_pts


async def update_player_skill_pts(steamid: str | int, from_local=False, update_steam_info=True):
    if from_local:
        records = await fetch_pb_records(steamid)
    else:
        records = await get_personal_all_records(steamid, 'kz_timer', True)
        records = filter_pb_records(records)

    if not records:
        logger.debug(f"No records found for {steamid}")
        return

    player_data = calc_skill_pts(records)
    await update_player_rank(player_data, update_steam_info=update_steam_info)
