import aiomysql

from app import logger
from config import DB2_CONFIG, MAP_TIERS
from app.core.utils.steam_user import conv_steamid


async def get_latest_record_id():
    async with aiomysql.connect(**DB2_CONFIG) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id FROM records ORDER BY id DESC LIMIT 1"
            )
            latest_id = await cur.fetchone()
            return latest_id[0]


def filter_pb_records(records):
    pb_records = []
    records_by_map = {}
    for record in records:
        if record['map_name'] not in MAP_TIERS.keys():
            continue
        if record['map_name'] not in records_by_map:
            records_by_map[record['map_name']] = {'tp': None, 'pro': None}

        if record['teleports'] > 0:
            if records_by_map[record['map_name']]['tp'] is None or record['time'] < records_by_map[record['map_name']]['tp']['time']:
                records_by_map[record['map_name']]['tp'] = record
        else:
            if records_by_map[record['map_name']]['pro'] is None or record['time'] < records_by_map[record['map_name']]['pro']['time']:
                records_by_map[record['map_name']]['pro'] = record

    for map_name, records in records_by_map.items():
        if records['tp'] is not None:
            pb_records.append(records['tp'])
        if records['pro'] is not None:
            pb_records.append(records['pro'])

    return pb_records


async def fetch_pb_records(steam_id, mode='kz_timer'):
    records = await fetch_personal_records(steam_id, mode)
    return filter_pb_records(records)


async def fetch_personal_records(steam_id, mode=None, map_name=None, has_tp=None):
    logger.debug(f"Fetching records for {steam_id}")
    steam_id = conv_steamid(steam_id)
    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        select_query = f"""
            SELECT id, player_name, steam_id, server_id, map_id, stage, mode, `time`, teleports, created_on, server_name, map_name, points
            FROM records
            WHERE steam_id = %s AND stage = 0
        """
        params = [steam_id]

        if mode is not None:
            select_query += " AND mode = %s"
            params.append(mode)

        if map_name is not None:
            select_query += " AND map_name = %s"
            params.append(map_name)

        if has_tp is True:
            select_query += " AND teleports > 0"
        elif has_tp is False:
            select_query += " AND teleports = 0"

        await cursor.execute(select_query, params)
        records = await cursor.fetchall()
    conn.close()
    logger.debug(f"Fetched {len(records)} records for {steam_id}")
    return records


async def get_players_steamids(mode='kz_timer', limit=100, offset=0):
    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        select_query = f"""
            SELECT DISTINCT steam_id
            FROM records
            WHERE mode = %s
            LIMIT %s OFFSET %s
        """
        await cursor.execute(select_query, (mode, limit, offset))

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
