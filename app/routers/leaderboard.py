from fastapi import APIRouter, Path, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.core.database.leaderboard import query_leaderboard, query_player_rank, search_player_by_name
from app.core.skill_points.update import update_player_skill_pts
from app.core.utils.steam_user import conv_steamid
import redis.asyncio as redis
import json
from datetime import datetime

router = APIRouter()
EXPIRES_IN = 86400  # 24 hours

redis_client = redis.from_url("redis://localhost:6379", encoding="utf-8", decode_responses=True)


async def get_redis_conn():
    return redis_client


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


@router.get('/leaderboard')
async def leaderboard(offset: int = 0, limit: int = 20, mode='kz_timer', redis=Depends(get_redis_conn)):
    if limit > 1000:
        limit = 1000

    cache_key = f"leaderboard:{offset}:{limit}:{mode}"
    cached_data = await redis.get(cache_key)
    if cached_data:
        return JSONResponse(content=json.loads(cached_data))

    data = await query_leaderboard(offset, limit, mode=mode)
    await redis.set(cache_key, json.dumps(data, cls=CustomJSONEncoder), ex=EXPIRES_IN)  # Cache for 24 hours

    return data


@router.get('/leaderboard/{steamid}')
async def player_rank(
    steamid: str = Path(..., example="STEAM_1:0:530988200"),
    mode='kz_timer',
    redis=Depends(get_redis_conn)
):
    cache_key = f"player_rank:{steamid}:{mode}"
    cached_data = await redis.get(cache_key)
    if cached_data:
        return JSONResponse(content=json.loads(cached_data))

    data = await query_player_rank(steamid=steamid, mode=mode)
    if data is None:
        raise HTTPException(status_code=404, detail="Player not found")
    await redis.set(cache_key, json.dumps(data, cls=CustomJSONEncoder), ex=EXPIRES_IN)  # Cache for 24 hours

    return data


@router.get('/leaderboard/search/{nickname}')
async def search_player(nickname: str, redis=Depends(get_redis_conn)):
    cache_key = f"search_player:{nickname}"
    cached_data = await redis.get(cache_key)
    if cached_data:
        return JSONResponse(content=json.loads(cached_data))

    data = await search_player_by_name(nickname)
    await redis.set(cache_key, json.dumps(data, cls=CustomJSONEncoder), ex=EXPIRES_IN)  # Cache for 24 hours

    return data


@router.put('/leaderboard/{steamid}')
async def update_player_rank(
    steamid: str = Path(..., example="STEAM_1:0:530988200"),
    mode='kz_timer',
    redis=Depends(get_redis_conn)
):
    steamid = conv_steamid(steamid)
    before = await query_player_rank(steamid=steamid)
    await update_player_skill_pts(steamid=steamid, mode=mode)
    after = await query_player_rank(steamid=steamid)

    await redis.delete(f"player_rank:{steamid}:{mode}")
    return {'before': before, 'after': after}
