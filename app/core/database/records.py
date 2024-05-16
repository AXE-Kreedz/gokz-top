import aiomysql

from config import DB2_CONFIG
from app.core.utils.steam_user import conv_steamid


async def get_latest_record_id():
    async with aiomysql.connect(**DB2_CONFIG) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id FROM records ORDER BY id DESC LIMIT 1"
            )
            latest_id = await cur.fetchone()
            return latest_id[0]


async def fetch_tp_pb_records(steam_id):
    steam_id = conv_steamid(steam_id)
    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        select_query = f"""
            SELECT r.id, r.player_name, r.steam_id, r.server_id, r.map_id, r.stage, r.mode, r.`time`, r.teleports, r.created_on, r.server_name, r.map_name, r.points
            FROM records r
            INNER JOIN (
                SELECT map_name, mode, MIN(`time`) as min_time
                FROM records
                WHERE steam_id = %s AND stage = 0
                GROUP BY map_name, mode
            ) pb ON r.map_name = pb.map_name AND r.mode = pb.mode AND r.`time` = pb.min_time
            WHERE r.steam_id = %s AND r.stage = 0
        """
        await cursor.execute(select_query, (steam_id, steam_id))
        records = await cursor.fetchall()
    conn.close()
    return records


async def fetch_personal_records(steam_id):
    steam_id = conv_steamid(steam_id)
    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        select_query = f"""
            SELECT id, player_name, steam_id, server_id, map_id, stage, mode, `time`, teleports, created_on, server_name, map_name, points
            FROM records
            WHERE steam_id = %s AND stage = 0
        """
        await cursor.execute(select_query, steam_id)
        records = await cursor.fetchall()
    conn.close()
    return records


async def get_players_steamids():
    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        select_query = """
            SELECT DISTINCT steam_id
            FROM records
        """
        await cursor.execute(select_query)
        steam_ids = [row['steam_id'] for row in await cursor.fetchall()]
    conn.close()
    return steam_ids


async def insert_records(records: list[dict] | dict):
    if not records:
        return

    if isinstance(records, dict):
        records = [records]

    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        records_data = [
            (
                record["id"],
                record["steamid64"],
                record["player_name"],
                record["steam_id"],
                record["server_id"],
                record["map_id"],
                record["stage"],
                record["mode"],
                record["tickrate"],
                record["time"],
                record["teleports"],
                record["created_on"],
                record["updated_on"],
                record["updated_by"],
                record["record_filter_id"],
                record["server_name"],
                record["map_name"],
                record["points"],
                record["replay_id"],
            )
            for record in records
            if record
        ]

        insert_query = f"""
            INSERT INTO records (
                id, steamid64, player_name, steam_id, server_id, map_id,
                stage, mode, tickrate, time, teleports, created_on, updated_on,
                updated_by, record_filter_id, server_name, map_name, points,
                replay_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) AS new
            ON DUPLICATE KEY UPDATE
                steamid64 = new.steamid64,
                player_name = new.player_name,
                steam_id = new.steam_id,
                server_id = new.server_id,
                map_id = new.map_id,
                stage = new.stage,
                mode = new.mode,
                tickrate = new.tickrate,
                time = new.time,
                teleports = new.teleports,
                created_on = new.created_on,
                updated_on = new.updated_on,
                updated_by = new.updated_by,
                record_filter_id = new.record_filter_id,
                server_name = new.server_name,
                map_name = new.map_name,
                points = new.points,
                replay_id = new.replay_id
        """

        await cursor.executemany(insert_query, records_data)
        await conn.commit()
    conn.close()


async def update_points(records):
    if not records:
        return

    if isinstance(records, dict):
        records = [records]

    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        ids = []
        cases = []
        for record in records:
            ids.append(str(record["id"]))
            cases.append(f"WHEN id = {record['id']} THEN {record['points']}")

        update_query = f"""
            UPDATE records
            SET points = CASE {' '.join(cases)} END
            WHERE id IN ({', '.join(ids)})
        """
        await cursor.execute(update_query)
        await conn.commit()
