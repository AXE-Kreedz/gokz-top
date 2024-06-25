"""
Show the Rank / Top% / Rating
Player Name / Avatar
🥇🥈🥉
"""
import asyncio

from app.core.database.leaderboard import search_player_by_name, query_player_rank
from app.core.database.records import fetch_pb_records
from app.core.utils.kreedz import get_vnl_map_tier, get_map_tier
from app.core.utils.steam_user import conv_steamid


total_maps = {
    'kz_timer': {
        'tp': {
            1: 121,
            2: 272,
            3: 239,
            4: 150,
            5: 65,
            6: 63,
            7: 23,
            'total': 933
        },
        'pro': {
            1: 121,
            2: 272,
            3: 240,
            4: 151,
            5: 66,
            6: 64,
            7: 24,
            'total': 938
        }
    },
    'kz_simple': {
        'tp': {
            1: 122,
            2: 272,
            3: 235,
            4: 142,
            5: 64,
            6: 60,
            7: 22,
            'total': 917
        },
        'pro': {
            1: 122,
            2: 272,
            3: 236,
            4: 143,
            5: 65,
            6: 61,
            7: 23,
            'total': 922
        },
    },
    'kz_vanilla': {
        'tp': {
            1: 32,
            2: 103,
            3: 118,
            4: 109,
            5: 66,
            6: 49,
            7: 54,
            'total': 531
        },
        'pro': {
            1: 32,
            2: 103,
            3: 118,
            4: 109,
            5: 66,
            6: 49,
            7: 54,
            'total': 531
        }
    }
}


class Stats:
    def __init__(self, steamid, mode='kz_timer'):
        self.steamid: str = conv_steamid(steamid)
        self.steamid64: str = str(conv_steamid(self.steamid, 64))
        self.mode: str = mode

        self.name = None
        self.avatar_hash = None
        self.rank_name = None
        self.rank = None
        self.percentage = None
        self.rating = None
        self.most_played_server = None

        self.stats = None
        self.records: list = []
        self.total_maps = total_maps[mode]

    async def init(self):
        rank_data = await query_player_rank(steamid=self.steamid, mode=self.mode)
        records = await fetch_pb_records(self.steamid, self.mode)

        if not rank_data:
            rank_data = {}

        self.name = rank_data.get('name', 'Anonymous')  # If 'name' key doesn't exist, 'Anonymous' will be used
        self.avatar_hash = rank_data.get('avatar_hash', '')
        self.rank_name = rank_data.get('rank_name', 'New')
        self.rank = rank_data.get('rank', 0)
        self.percentage = rank_data.get('percentage', 0.0)
        self.rating = rank_data.get('pts_skill', 0.0)
        self.most_played_server = rank_data.get('most_played_server', '')

        self.records = records if records else []
        self.stats = calc_player_data(self.records) if self.records else {}


def calc_player_data(rcds):
    pts_avgs = {'tp': {}, 'pro': {}}
    counts = {}

    get_map_tier_func = get_vnl_map_tier if rcds[0]['mode'] == 'kz_vanilla' else get_map_tier

    def tier_calc(cate_str):
        is_tp = True if cate_str == 'tp' else False
        for tier in range(1, 8):
            tier_records = [rcd for rcd in rcds if get_map_tier_func(rcd['map_name']) == tier and (rcd['teleports'] > 0 if is_tp else rcd['teleports'] == 0)]
            pts_avgs[cate_str][f"avg_{tier}"] = int(sum(rcd['points'] for rcd in tier_records) / len(tier_records) if tier_records else 0)
            pts_avgs[cate_str][f"count_{tier}"] = len(set(rcd['map_name'] for rcd in tier_records))

    for category in ['tp', 'pro']:
        tier_calc(category)

    counts.update({
        'count_p1000_tp': sum(1 for rcd in rcds if rcd['points'] == 1000 and rcd['teleports'] > 0),
        'count_p1000_pro': sum(1 for rcd in rcds if rcd['points'] == 1000 and rcd['teleports'] == 0),

        'count_p900_tp': sum(1 for rcd in rcds if 1000 > rcd['points'] >= 900 and rcd['teleports'] > 0),
        'count_p900_pro': sum(1 for rcd in rcds if 1000 > rcd['points'] >= 900 and rcd['teleports'] == 0),
        'count_p800_tp': sum(1 for rcd in rcds if 900 > rcd['points'] >= 800 and rcd['teleports'] > 0),
        'count_p800_pro': sum(1 for rcd in rcds if 900 > rcd['points'] >= 800 and rcd['teleports'] == 0),
        'count': len(set(rcd['map_name'] for rcd in rcds)),
    })

    pts_avgs['pts_avg'] = int(sum(rcd['points'] for rcd in rcds) / len(rcds) if rcds else 0)  # NOQA
    counts['count_pro'] = sum(1 for rcd in rcds if rcd['teleports'] == 0)
    counts['count_tp'] = sum(1 for rcd in rcds if rcd['teleports'] > 0)

    pts_avgs['pts_avg_pro'] = int(sum(rcd['points'] for rcd in rcds if rcd['teleports'] == 0) / counts['count_pro']) if counts['count_pro'] else 0
    pts_avgs['pts_avg_tp'] = int(sum(rcd['points'] for rcd in rcds if rcd['teleports'] > 0) / counts['count_tp']) if counts['count_tp'] else 0
    pts_avgs['total_points'] = sum(rcd['points'] for rcd in rcds)

    return {**pts_avgs, **counts}


async def main():
    stats = Stats(steamid='1061976400')
    await stats.init()
    print(stats.__dict__)


if __name__ == '__main__':
    asyncio.run(main())
