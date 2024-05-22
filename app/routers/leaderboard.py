from fastapi import APIRouter, Path
from steam.steamid import from_url

from app.core.database.leaderboard import query_leaderboard, query_player_rank, search_player_by_name
from app.core.skill_points.update import update_player_skill_pts
from app.core.utils.steam_user import conv_steamid

router = APIRouter()


@router.get('/leaderboard')
async def leaderboard(offset: int = 0, limit: int = 20, mode='kz_timer'):
    if limit > 1000:
        limit = 1000
    return await query_leaderboard(offset, limit, mode=mode)


@router.get('/leaderboard/{steamid}')
async def player_rank(
    steamid: str = Path(..., example="STEAM_1:0:530988200"),
    mode='kz_timer'
):
    return await query_player_rank(steamid=steamid, mode=mode)


@router.get('/leaderboard/search/{nickname}')
async def search_player(nickname: str):
    return await search_player_by_name(nickname)


@router.put('/leaderboard/{steamid}')
async def update_player_rank(
    steamid: str = Path(..., example="STEAM_1:0:530988200"),
    mode='kz_timer'
):
    steamid = conv_steamid(steamid)
    before = await query_player_rank(steamid=steamid)
    await update_player_skill_pts(steamid=steamid)
    after = await query_player_rank(steamid=steamid)
    return {'before': before, 'after': after}
