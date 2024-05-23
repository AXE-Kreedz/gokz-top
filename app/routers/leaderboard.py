from fastapi import APIRouter, Path, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.core.database.leaderboard import query_leaderboard, query_player_rank, search_player_by_name
from app.core.middleware.redis_cache import get_redis_conn, DateTimeEncoder
from app.core.skill_points.update import update_player_skill_pts
from app.core.utils.steam_user import conv_steamid
import json

router = APIRouter()


@router.get('/leaderboard')
async def leaderboard(offset: int = 0, limit: int = 20, mode='kz_timer', redis=Depends(get_redis_conn)):
    if limit > 1000:
        limit = 1000

    cache_key = f"leaderboard:{offset}:{limit}:{mode}"
    cached_data = await redis.get(cache_key)
    if cached_data:
        return JSONResponse(content=json.loads(cached_data))

    data = await query_leaderboard(offset, limit, mode=mode)
    await redis.set(cache_key, json.dumps(data, cls=DateTimeEncoder))
    return data


@router.get('/leaderboard/{steamid}')
async def player_rank(steamid: str = Path(..., example="STEAM_1:0:530988200"), mode='kz_timer', redis=Depends(get_redis_conn)):
    cache_key = f"player_rank:{steamid}:{mode}"
    cached_data = await redis.get(cache_key)
    if cached_data:
        return JSONResponse(content=json.loads(cached_data))

    data = await query_player_rank(steamid=steamid, mode=mode)
    if data is None:
        raise HTTPException(status_code=404, detail="Player not found")
    await redis.set(cache_key, json.dumps(data, cls=DateTimeEncoder))
    return data


@router.get('/leaderboard/search/{nickname}')
async def search_player(nickname: str, redis=Depends(get_redis_conn)):
    cache_key = f"search_player:{nickname}"
    cached_data = await redis.get(cache_key)
    if cached_data:
        return JSONResponse(content=json.loads(cached_data))

    data = await search_player_by_name(nickname)
    await redis.set(cache_key, json.dumps(data, cls=DateTimeEncoder))
    return data


@router.put('/leaderboard/{steamid}')
async def update_player_rank(steamid: str = Path(..., example="STEAM_1:0:530988200"), mode='kz_timer', redis=Depends(get_redis_conn)):
    steamid = conv_steamid(steamid)
    before = await query_player_rank(steamid=steamid)
    await update_player_skill_pts(steamid=steamid, mode=mode)
    after = await query_player_rank(steamid=steamid)

    await redis.delete(f"player_rank:{steamid}:{mode}")
    return {'before': before, 'after': after}