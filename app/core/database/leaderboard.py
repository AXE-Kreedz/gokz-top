import aiomysql

from app.core.utils.steam_user import conv_steamid
from config import DB2_CONFIG

TOLERANCE = 0.00001
TOTAL_PLAYER = {
    'kz_timer': 225245,
    'kz_simple': 225245,
    'kz_vanilla': 225245,
}


async def get_all_points(mode='kz_timer'):
    table_name = get_table_name(mode)
    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor() as cursor:
        query = f"""
            SELECT pts_skill FROM {table_name}
        """
        await cursor.execute(query)
        result = await cursor.fetchall()
    conn.close()
    result = [row[0] for row in result]
    return result


def get_table_name(mode):
    if mode == 'kz_timer':
        return 'leaderboard'
    elif mode == 'kz_simple':
        return 'leaderboard_skz'
    elif mode == 'kz_vanilla':
        return 'leaderboard_vnl'


async def search_player_by_name(name) -> list:
    try:
        steamid = conv_steamid(name)
    except ValueError:
        steamid = None
    if steamid:
        data = await query_player_rank(steamid)
        if data:
            return [{
                'name': data['name'],
                'steamid': data['steamid'],
                'pts_skill': data['pts_skill'],
                'avatar_hash': data['avatar_hash'],
                'steamid64': str(conv_steamid(data['steamid'], 64)),
            }]

    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        # Query for exact matches
        exact_query = """
            SELECT name, steamid, pts_skill, avatar_hash FROM leaderboard
            WHERE name = %s LIMIT 10
        """
        await cursor.execute(exact_query, (name,))
        exact_result = await cursor.fetchall()

        startswith_query = """
            SELECT name, steamid, pts_skill, avatar_hash FROM leaderboard
            WHERE name LIKE %s LIMIT 10
        """
        await cursor.execute(startswith_query, (name + '%',))
        startswith_result = await cursor.fetchall()

        # Query for partial matches
        partial_query = """
            SELECT name, steamid, pts_skill, avatar_hash FROM leaderboard
            WHERE name LIKE %s LIMIT 10
        """
        await cursor.execute(partial_query, ('%' + name + '%',))
        partial_result = await cursor.fetchall()
    conn.close()

    exact_result = list(exact_result)
    startswith_result = list(startswith_result)
    partial_result = list(partial_result)
    all_results = exact_result + startswith_result + partial_result
    unique_results = {player['steamid']: player for player in all_results}
    result = list(unique_results.values())[:10]

    for player in result:
        player['steamid64'] = str(conv_steamid(player['steamid'], 64))
    return result


async def get_steamids_with_empty_avatar():
    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor() as cursor:
        query = """
            SELECT steamid FROM leaderboard
            WHERE avatar_hash = ''
            ORDER BY pts_skill DESC
        """
        await cursor.execute(query)
        result = await cursor.fetchall()
    conn.close()
    return [row[0] for row in result]


async def update_avatar_hash(steamid, avatar_hash):
    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor() as cursor:
        query = """
            UPDATE leaderboard
            SET avatar_hash = %s
            WHERE steamid = %s
        """
        await cursor.execute(query, (avatar_hash, steamid))
        await conn.commit()
    conn.close()


async def update_player_rank(player_data, mode='kz_timer'):
    table_name = get_table_name(mode)
    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor() as cursor:
        insert_query = f"""
            INSERT INTO {table_name} (
                steamid, name, pts_skill, rank_name, most_played_server, avatar_hash, pts_avg_t5, pts_avg_t6, pts_avg_t7, pts_avg,
                pts_avg_pro, pts_avg_tp, total_points, count_t5, count_t6, count_t7, count_p1000_tp, count_p1000_pro,
                count_p900, count_p800, count, count_t567_p900, count_t567_p800, count_t567_pro, count_pro, count_tp
            ) VALUES (
                %(steamid)s, %(name)s, %(pts_skill)s, %(rank_name)s, %(most_played_server)s, %(avatar_hash)s, %(pts_avg_t5)s, %(pts_avg_t6)s,
                %(pts_avg_t7)s, %(pts_avg)s, %(pts_avg_pro)s, %(pts_avg_tp)s, %(total_points)s, %(count_t5)s,
                %(count_t6)s, %(count_t7)s, %(count_p1000_tp)s, %(count_p1000_pro)s, %(count_p900)s, %(count_p800)s,
                %(count)s, %(count_t567_p900)s, %(count_t567_p800)s, %(count_t567_pro)s, %(count_pro)s, %(count_tp)s
            ) AS new
            ON DUPLICATE KEY UPDATE
                name = new.name,
                pts_skill = new.pts_skill,
                rank_name = new.rank_name,
                most_played_server = new.most_played_server,
                avatar_hash = IF(new.avatar_hash = '', {table_name}.avatar_hash, new.avatar_hash),
                pts_avg_t5 = new.pts_avg_t5,
                pts_avg_t6 = new.pts_avg_t6,
                pts_avg_t7 = new.pts_avg_t7,
                pts_avg = new.pts_avg,
                pts_avg_pro = new.pts_avg_pro,
                pts_avg_tp = new.pts_avg_tp,
                total_points = new.total_points,
                count_t5 = new.count_t5,
                count_t6 = new.count_t6,
                count_t7 = new.count_t7,
                count_p1000_tp = new.count_p1000_tp,
                count_p1000_pro = new.count_p1000_pro,
                count_p900 = new.count_p900,
                count_p800 = new.count_p800,
                count = new.count,
                count_t567_p900 = new.count_t567_p900,
                count_t567_p800 = new.count_t567_p800,
                count_t567_pro = new.count_t567_pro,
                count_pro = new.count_pro,
                count_tp = new.count_tp
        """
        await cursor.execute(insert_query, player_data)
        await conn.commit()
    conn.close()


async def query_leaderboard(offset=0, limit=20, mode='kz_timer'):
    table_name = get_table_name(mode)
    total_player = TOTAL_PLAYER[mode]

    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        query = f"""
            SELECT * FROM {table_name}
            ORDER BY pts_skill DESC, steamid DESC
            LIMIT %s OFFSET %s
        """
        await cursor.execute(query, (limit, offset))
        result = await cursor.fetchall()
    conn.close()
    for i, player in enumerate(result, start=offset + 1):
        player['pts_skill'] = int(player['pts_skill'] * 100) / 100.0
        player['rank'] = i
        player['percentage'] = "{:.3%}".format(i / total_player)
        player['steamid64'] = str(conv_steamid(player['steamid'], 64))
    return result


async def query_player_rank(steamid, mode='kz_timer'):
    table_name = get_table_name(mode)
    steamid = conv_steamid(steamid)
    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        player_query = f"""
            SELECT * FROM {table_name}
            WHERE steamid = %s
        """
        await cursor.execute(player_query, (steamid,))
        player = await cursor.fetchone()

        if player is None:
            return None

        rank_query = f"""
            SELECT COUNT(*) as `rank` FROM {table_name}
            WHERE pts_skill > %s OR 
                  (pts_skill BETWEEN %s AND %s AND steamid > %s)
        """

        await cursor.execute(rank_query, (player['pts_skill'] + 0.00001,
                                          player['pts_skill'] - TOLERANCE,
                                          player['pts_skill'] + TOLERANCE,
                                          steamid
                                          ))
        rank = await cursor.fetchone()

    conn.close()

    player['rank'] = rank['rank'] + 1

    total_player = TOTAL_PLAYER[mode]
    player['pts_skill'] = int(player['pts_skill'] * 100) / 100.0
    player['percentage'] = "{:.3%}".format(player['rank'] / total_player)
    player['steamid64'] = str(conv_steamid(player['steamid'], 64))
    return player


async def get_total_players(mode='kz_timer'):
    table_name = get_table_name(mode)
    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor() as cursor:
        query = f"""
            SELECT COUNT(steamid) FROM {table_name}
        """
        await cursor.execute(query)
        result = await cursor.fetchone()
    conn.close()
    return result[0] if result else 0
