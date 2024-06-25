from datetime import datetime

import pytz
from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
from fastapi import APIRouter, Path, Depends, HTTPException

from app import logger
from app.core.database.leaderboard import query_leaderboard, query_player_rank, search_player_by_name
from app.core.database.records import fetch_personal_records, fetch_pb_records, get_record_by_server_id
from app.core.globalapi.stats import Stats
from app.core.middleware.redis_cache import get_redis_conn
from app.core.skill_points.update import update_player_skill_pts
from app.core.utils.format import format_kzmode
from app.core.utils.steam_user import conv_steamid
from config import WEBHOOK_URL

router = APIRouter()


@router.get("/records/stats/{steamid}")
async def get_player_stats(steamid: str = Path(..., example="STEAM_1:0:530988200"), mode: str = 'kz_timer'):
    mode = format_kzmode(mode)
    stats = Stats(steamid=steamid, mode=mode)
    await stats.init()
    return stats.__dict__


@router.get('/records/{steamid}')
async def player_records(steamid: str = Path(..., example="STEAM_1:0:530988200"), mode: str = 'kz_timer', map_name: str = None, has_tp: bool = None):
    steamid = conv_steamid(steamid)
    records = await fetch_personal_records(steamid, mode, map_name=map_name, has_tp=has_tp)
    return records


@router.get('/records/top/{steamid}')
async def player_pb_records(steamid: str = Path(..., example="STEAM_1:0:530988200"), mode: str = 'kz_timer', map_name: str = None, has_tp: bool = None):
    steamid = conv_steamid(steamid)
    records = await fetch_pb_records(steamid, mode, map_name=map_name, has_tp=has_tp)
    return records


@router.get('/records')
async def player_records(server_id=1683):
    records = await get_record_by_server_id(server_id=server_id)

    tz = pytz.timezone('Asia/Shanghai')
    for record in records:
        created_on_utc = datetime.strptime(record['created_on'], '%Y-%m-%dT%H:%M:%S')
        created_on_local = created_on_utc.replace(tzinfo=pytz.utc).astimezone(tz)
        record['created_on'] = created_on_local.strftime('%Y-%m-%d %H:%M:%S')

    return records


@router.get('/leaderboard')
async def leaderboard(offset: int = 0, limit: int = 20, mode='kz_timer', redis=Depends(get_redis_conn)):
    mode = format_kzmode(mode)
    if limit > 1000:
        limit = 1000

    # cache_key = f"leaderboard:{offset}:{limit}:{mode}"
    # cached_data = await redis.get(cache_key)
    # if cached_data:
    #     return JSONResponse(content=json.loads(cached_data))

    data = await query_leaderboard(offset, limit, mode=mode)
    # await redis.set(cache_key, json.dumps(data, cls=DateTimeEncoder))
    return data


@router.get('/leaderboard/{steamid}')
async def player_rank(steamid: str = Path(..., example="STEAM_1:0:530988200"), mode='kz_timer', redis=Depends(get_redis_conn)):
    mode = format_kzmode(mode)

    # cache_key = f"player_rank:{steamid}:{mode}"
    # cached_data = await redis.get(cache_key)
    # if cached_data:
    #     data = json.loads(cached_data)
    #     await send_webhook(title=data['name'], content=f"Rank: `{data['rank']}`\nsteamid64: `{data['steamid64']}`",
    #                        avatar=data['avatar_hash'], url='https://steamcommunity.com/profiles/' + data['steamid64'])
    #     return JSONResponse(content=data)

    data = await query_player_rank(steamid=steamid, mode=mode)
    if data is None:
        raise HTTPException(status_code=404, detail="Player not found")

    # await redis.set(cache_key, json.dumps(data, cls=DateTimeEncoder))
    #
    # await send_webhook(title=data['name'], content=f"Rank: `{data['rank']}`\nsteamid64: `{data['steamid64']}`",
    #                    avatar=data['avatar_hash'], url='https://steamcommunity.com/profiles/' + data['steamid64'])

    return data


@router.get('/leaderboard/search/{nickname}')
async def search_player(nickname: str, mode='kz_timer', redis=Depends(get_redis_conn)):
    mode = format_kzmode(mode)

    # cache_key = f"search_player:{nickname}:{mode}"
    # cached_data = await redis.get(cache_key)
    # if cached_data:
    #     return JSONResponse(content=json.loads(cached_data))

    data = await search_player_by_name(nickname, mode=mode)
    # await redis.set(cache_key, json.dumps(data, cls=DateTimeEncoder))
    return data


@router.put('/leaderboard/{steamid}', include_in_schema=False)
async def update_player_rank(steamid: str = Path(..., example="STEAM_1:0:530988200"), mode='kz_timer', redis=Depends(get_redis_conn)):
    mode = format_kzmode(mode)
    steamid = conv_steamid(steamid)

    before = await query_player_rank(steamid=steamid)
    await update_player_skill_pts(steamid=steamid, mode=mode)
    after = await query_player_rank(steamid=steamid)

    # await redis.delete(f"player_rank:{steamid}:{mode}")

    page_size = 30

    if before is None:
        return {'before': None, 'after': after}

    # if before['rank'] != after['rank']:
    #     start_of_rank_page = min(before['rank'], after['rank']) // page_size * page_size
    #     end_of_rank_page = max(before['rank'], after['rank']) // page_size * page_size
    #     all_cache_keys = await redis.keys(f"leaderboard:*:*:{mode}")
    #     for key in all_cache_keys:
    #         try:
    #             offset = int(key.split(':')[1])
    #             if start_of_rank_page <= offset < end_of_rank_page:
    #                 await redis.delete(key)
    #         except ValueError:
    #             continue
    #
    # else:
    #     cache_key = f"leaderboard:{before['rank'] // page_size * page_size}:{page_size}:{mode}"
    #     await redis.delete(cache_key)

    return {'before': before, 'after': after}


async def send_webhook(title, content, url=None, avatar=None):
    try:
        avatar_url = None
        if avatar is not None:
            avatar_url = f"https://avatars.cloudflare.steamstatic.com/{avatar}_full.jpg"
        embed = DiscordEmbed(title=title, description=content, color=0x03b2f8, url=url)
        if avatar_url is not None:
            embed.set_thumbnail(url=avatar_url)
        webhook = AsyncDiscordWebhook(url=WEBHOOK_URL, embeds=[embed])
        await webhook.execute()
    except Exception as e:
        logger.warning(f"Failed to send webhook: {e}")
        return False
