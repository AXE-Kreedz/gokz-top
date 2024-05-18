import asyncio

import aiohttp
from aiohttp import ClientTimeout
from steam.steamid import SteamID

from app import logger
from config import STEAM_API_KEY


def conv_steamid(steamid, target_type: int = 2, url=False):
    steamid = SteamID(steamid)
    if steamid.is_valid() is False:
        raise ValueError(f"Invalid SteamID: {steamid}")

    if url:
        return steamid.community_url

    target_type = int(target_type)

    if target_type == 2:
        return steamid.as_steam2
    if target_type == 3:
        return steamid.as_steam3
    if target_type == 32:
        return steamid.as_32
    if target_type == 64:
        return steamid.as_64
    if target_type == 0:
        return {
            "steam2": steamid.as_steam2,
            "steam3": steamid.as_steam3,
            "steam64": steamid.as_64,
            "steam32": steamid.as_32,
            "url": steamid.community_url,
        }

    raise ValueError(f"Invalid target type: {target_type}")


async def get_steam_user_info(steamid, timeout=5.0) -> dict | None:
    """
        Get information about a Steam user using their SteamID64.
        Returns:
            {
                'steamid': str,
                'communityvisibilitystate': int,
                'profilestate': int,
                'personaname': str,
                'commentpermission': int,
                'profileurl': str,
                'avatar': str,
                'avatarmedium': str,
                'avatarfull': str,
                'avatarhash': str,
                'lastlogoff': int,
                'personastate': int,
                'primaryclanid': str,
                'timecreated': int,
                'personastateflags': int,
                'loccountrycode': str,
                'locstatecode': str,
                'loccityid': int
            }
    """
    steamid = conv_steamid(steamid, 64)

    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM_API_KEY}&steamids={steamid}"

    try:
        async with aiohttp.ClientSession(timeout=ClientTimeout(timeout)) as session:
            async with session.get(url, ssl=False) as response:
                try:
                    data = await response.json()
                except aiohttp.client_exceptions.ContentTypeError:
                    return None
    except asyncio.TimeoutError:
        logger.warning(f"get_steam_user_info: Timeout for {steamid}")
        return None

    try:
        player_data = data['response']['players'][0]
        return player_data
    except IndexError:
        logger.warning(f"get_steam_user_info: No player found for {steamid}:\n{data}")
        return None
