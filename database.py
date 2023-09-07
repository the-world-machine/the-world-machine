import aiomysql
from load_data import *
from interactions import *
import asyncio

ip = load_config('PHPma-IP')
user = load_config('PHPma-USERNAME')
password = load_config('PHPma-PASSWORD')
db_name = load_config('PHPma-DBNAME')

cursor: aiomysql.Cursor = None

async def load_database():

    global cursor

    connection: aiomysql.Connection = await aiomysql.connect(
        host=ip,
        user=user,
        password=password,
        db=db_name,
        autocommit=True
    )

    cursor = await connection.cursor()

    print('Database connected.')


def get_datatype(data):
    if type(data) == str:
        return f"{data}"

    if type(data) == list:
        return json.dumps(data)

    if type(data) == bool:
        return json.dumps({'bool_value': data})

    return data


async def get_leaderboard(sort_by: str):

    sql = 'SELECT p_key, wool FROM user_data ORDER BY {0} DESC LIMIT 10;'.format(sort_by)
    await cursor.execute(sql)

    return await cursor.fetchall()


async def get(table: str, primary_key, columns: str):

    p_key = primary_key

    if type(primary_key) == Snowflake:
        p_key = int(primary_key)

    select_sql = f"SELECT * FROM `{table}` WHERE p_key = {p_key}"

    try:
        await cursor.execute(select_sql)
    except:
        await new_entry(table, p_key)

    row = await cursor.fetchone()

    value = None

    if row:

        for i, column_name in enumerate(cursor.description):

            if column_name[0] == columns:

                value = row[i]

                # List Handling.
                try:
                    value = json.loads(value)

                    if 'bool_value' in value:
                        value = value['bool_value']
                except:
                    pass

                break

        return value
    else:
        await new_entry(table, p_key)
        return await get(table, p_key, columns)


async def new_entry(table: str, primary_key: int):
    insert_sql = f'INSERT INTO `{table}` (p_key) VALUES ({primary_key})'
    await cursor.execute(insert_sql)


async def set(table: str, column: str, p_key, data):
    if not p_key:
        raise ValueError("Primary key is not set.")

    primary_key = p_key

    if type(p_key) == Snowflake:
        primary_key = int(p_key)

    d_type = get_datatype(data)

    # Check if the primary key already exists in the table
    select_sql = f"SELECT * FROM `{table}` WHERE p_key = %s"
    await cursor.execute(select_sql, (primary_key,))

    row = cursor.fetchone()

    if row:
        update_sql = f"UPDATE `{table}` SET `{column}` = %s WHERE p_key = %s"
        await cursor.execute(update_sql, (d_type, primary_key))
    else:
        insert_sql = f"INSERT INTO `{table}` (p_key, `{column}`) VALUES (%s, %s)"
        await cursor.execute(insert_sql, (primary_key, d_type))

    return await get(table, primary_key, column)


async def increment_value(table: str, column: str, primary_key: int):
    v: int = await get(table, primary_key, column)
    await set(table, column, primary_key, v + 1)
