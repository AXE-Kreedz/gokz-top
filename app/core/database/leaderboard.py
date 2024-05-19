import aiomysql

from app.core.utils.steam_user import conv_steamid
from config import DB2_CONFIG


async def update_player_rank(player_data):
    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor() as cursor:
        insert_query = """
            INSERT INTO leaderboard (
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
                avatar_hash = IF(new.avatar_hash = '', leaderboard.avatar_hash, new.avatar_hash),
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


async def query_leaderboard(offset=0, limit=20):
    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        query = """
            SELECT * FROM leaderboard
            ORDER BY pts_skill DESC
            LIMIT %s OFFSET %s
        """
        await cursor.execute(query, (limit, offset))
        result = await cursor.fetchall()
    conn.close()
    total_player = 400_000
    for i, player in enumerate(result, start=offset+1):
        player['pts_skill'] = int(player['pts_skill'] * 100) / 100.0
        player['rank'] = i
        player['percentage'] = "{:.3%}".format(i / total_player)
        player['steamid64'] = str(conv_steamid(player['steamid'], 64))
    return result


async def query_player_rank(steamid):
    steamid = conv_steamid(steamid)
    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        query = """
            SELECT * FROM (
                SELECT *, ROW_NUMBER() OVER (ORDER BY pts_skill DESC) as `rank`
                FROM leaderboard
            ) as leaderboard_with_ranks
            WHERE steamid = %s
        """
        await cursor.execute(query, (steamid,))
        result = await cursor.fetchone()
    conn.close()

    total_player = 400_000
    result['pts_skill'] = int(result['pts_skill'] * 100) / 100.0
    result['percentage'] = "{:.3%}".format(result['rank'] / total_player)
    result['steamid64'] = str(conv_steamid(result['steamid'], 64))
    return result if result else None


async def get_total_players():
    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor() as cursor:
        query = """
            SELECT COUNT(steamid) FROM leaderboard
        """
        await cursor.execute(query)
        result = await cursor.fetchone()
    conn.close()
    return result[0] if result else 0
