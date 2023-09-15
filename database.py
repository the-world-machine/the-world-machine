import mysql.connector as MySQLdb
import json
from load_data import load_config
from interactions import Snowflake

ip = load_config('PHPma-IP')
user = load_config('PHPma-USERNAME')
password = load_config('PHPma-PASSWORD')
db_name = load_config('PHPma-DBNAME')

db: MySQLdb.MySQLConnection = MySQLdb.connect(host=ip, user=user, password=password, database=db_name)
cursor = db.cursor()


async def get_datatype(data):
    if type(data) == str:
        return f"{data}"

    if type(data) == list:
        return json.dumps(data)

    if type(data) == bool:
        return json.dumps({'bool_value': data})

    return data


async def get_leaderboard(sort_by: str):
    sql = 'SELECT p_key, wool FROM user_data ORDER BY {0} DESC LIMIT 10;'.format(sort_by)
    cursor.execute(sql)

    return cursor.fetchall()


async def get(table: str, primary_key, columns: str):
    if type(primary_key) == Snowflake:
        primary_key = int(primary_key)

    select_sql = f"SELECT * FROM `{table}` WHERE p_key = {primary_key}"
    try:
        cursor.execute(select_sql)
    except:
        await new_entry('server_data', primary_key)

    row = cursor.fetchone()

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
        await new_entry(table, primary_key)
        return await get(table, primary_key, columns)


async def new_entry(table: str, primary_key: int):
    insert_sql = f'INSERT INTO `{table}` (p_key) VALUES ({primary_key})'
    cursor.execute(insert_sql)


async def set(table: str, column: str, p_key, data):
    if not p_key:
        raise ValueError("Primary key is not set.")

    if type(p_key) == Snowflake:
        p_key = int(p_key)

    d_type = await get_datatype(data)

    # Check if the primary key already exists in the table
    select_sql = f"SELECT * FROM `{table}` WHERE p_key = %s"
    cursor.execute(select_sql, (p_key,))

    row = cursor.fetchone()

    if row:
        update_sql = f"UPDATE `{table}` SET `{column}` = %s WHERE p_key = %s"
        cursor.execute(update_sql, (d_type, p_key))
    else:
        insert_sql = f"INSERT INTO `{table}` (p_key, `{column}`) VALUES (%s, %s)"
        cursor.execute(insert_sql, (p_key, d_type))

    try:
        db.commit()
    except Exception as e:
        print(f"Error committing changes to database: {e}")
        db.rollback()
        return None

    return await get(table, p_key, column)


async def increment_value(table: str, column: str, primary_key: int):
    v: int = await get(table, primary_key, column)
    await set(table, column, primary_key, v + 1)