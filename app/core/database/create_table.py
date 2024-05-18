import aiomysql

from config import DB2_CONFIG


tables = {
    'records': """
        CREATE TABLE IF NOT EXISTS records (
            id INT PRIMARY KEY,
            steamid64 VARCHAR(30),
            player_name VARCHAR(255),
            steam_id VARCHAR(30),
            server_id INT,
            map_id INT,
            stage TINYINT UNSIGNED,
            mode VARCHAR(15),
            tickrate INT,
            time FLOAT,
            teleports INT,
            created_on VARCHAR(30),
            updated_on VARCHAR(30),
            updated_by INT,
            record_filter_id INT,
            server_name VARCHAR(255),
            map_name VARCHAR(50),
            points INT,
            replay_id INT
        )
    """,
    'leaderboard': """
        CREATE TABLE IF NOT EXISTS leaderboard (
            steamid VARCHAR(30) PRIMARY KEY,
            name VARCHAR(255),
            pts_skill FLOAT,
            rank_name VARCHAR(30),
            most_played_server VARCHAR(255),
            avatar_hash VARCHAR(255),
            total_points INT,
            count INT,
            pts_avg INT,
            pts_avg_t5 INT,
            pts_avg_t6 INT,
            pts_avg_t7 INT,
            pts_avg_pro INT,
            pts_avg_tp INT,
            count_t5 INT,
            count_t6 INT,
            count_t7 INT,
            count_p1000_tp INT,
            count_p1000_pro INT,
            count_p900 INT,
            count_p800 INT,
            count_t567_p900 INT,
            count_t567_p800 INT,
            count_t567_pro INT,
            count_pro INT,
            count_tp INT
        )
    """,
}


async def create_table_if_not_exists(table_sql):
    conn = await aiomysql.connect(**DB2_CONFIG)
    async with conn.cursor() as cursor:

        await cursor.execute(table_sql)
        await conn.commit()
    conn.close()
