import json
from typing import Union
import aiomysql
from interactions import Snowflake, Extension, listen
from interactions.api.events import Startup
from load_data import load_config
from datetime import datetime

ip = load_config('PHPma-IP')
user = load_config('PHPma-USERNAME')
password = load_config('PHPma-PASSWORD')
db_name = load_config('PHPma-DBNAME')

class Database(Extension):
    pool: aiomysql.Pool = None  # class-level variable to store the database connection pool

    @staticmethod
    async def create_pool():
        
        if Database.pool is not None:
            return
        
        Database.pool = await aiomysql.create_pool(
            host=ip,
            port=3306,
            user=user,
            password=password,
            db=db_name,
            autocommit=True
        )

    @listen(Startup)
    async def on_ready(self):
        await Database.create_pool()

    @staticmethod
    async def execute(sql: str, *values: any):

        async with Database.pool.acquire() as conn:
            async with conn.cursor(aiomysql.Cursor) as cursor:
                await cursor.execute(sql, values)

        return cursor
    
    @staticmethod
    async def fetch_shop_data() -> dict:
        
        async with Database.pool.acquire() as conn:
            async with conn.cursor(aiomysql.Cursor) as cursor:
                await cursor.execute('SELECT * FROM shop_data')
                
                row = await cursor.fetchone()
                headers = cursor.description
                
        data = {}
        
        for i in range(len(row)):
            data[headers[i][0]] = row[i]
            
        return data

    @staticmethod
    async def fetch(table: str, column: str, primary_key: Union[int, Snowflake]) -> any:
        if type(primary_key) == Snowflake:
            primary_key = int(primary_key)

        select_sql = f"SELECT {column} FROM {table} WHERE p_key = {primary_key}"
        column_sql = f"DESCRIBE {table} {column}"

        async with Database.pool.acquire() as conn:
            async with conn.cursor(aiomysql.Cursor) as cursor:
                await cursor.execute(select_sql)

                row = await cursor.fetchone()

        async with Database.pool.acquire() as conn:
            async with conn.cursor(aiomysql.Cursor) as cursor:
                await cursor.execute(column_sql)

                column_data = await cursor.fetchone()

        if row:
            value = row[0]

            # List + Dictionary Handling.
            if column_data[1] == 'longtext' and value is not None:
                return json.loads(value)

            return value
        else:
            await Database.new_entry(table, primary_key)  # use Database.new_entry()
            return await Database.fetch(table, column, primary_key)  # use Database.fetch()

    @staticmethod
    async def new_entry(table: str, primary_key: int):
        insert_sql = f'INSERT INTO `{table}` (p_key) VALUES ({primary_key})'

        async with Database.pool.acquire() as conn:
            async with conn.cursor(aiomysql.Cursor) as cursor:
                await cursor.execute(insert_sql)

    @staticmethod
    async def update(table: str, column: str, p_key = None, data = None):
        if p_key is None:
            raise ValueError("Primary key is not set.")

        if type(data) == list:
            data = json.dumps(data)
        elif type(data) == dict:
            data = json.dumps(data)
        elif data is None:
            data = 'NULL'

        if type(p_key) == Snowflake:
            p_key = int(p_key)

        # Check if the primary key already exists in the table
        select_sql = f"SELECT * FROM `{table}` WHERE p_key = %s"
        async with Database.pool.acquire() as conn:
            async with conn.cursor(aiomysql.Cursor) as cursor:
                await cursor.execute(select_sql, (p_key,))

        row = await cursor.fetchall()

        if row:

            update_sql = f"UPDATE `{table}` SET `{column}` = %s WHERE p_key = %s"
            async with Database.pool.acquire() as conn:
                async with conn.cursor(aiomysql.Cursor) as cursor:
                    await cursor.execute(update_sql, (data, p_key))
        else:
            insert_sql = f"INSERT INTO `{table}` (p_key, `{column}`) VALUES (%s, %s)"
            async with Database.pool.acquire() as conn:
                async with conn.cursor(aiomysql.Cursor) as cursor:
                    await cursor.execute(insert_sql, (p_key, data))

                try:
                    await conn.commit()
                except Exception as e:
                    print(f"Error committing changes to database: {e}")
                    await conn.rollback()
                    return None

        return await Database.fetch(table, column, p_key)  # use Database.fetch()

    @staticmethod
    async def get_items(item: str):

        sql = f'SELECT * FROM {item}'

        async with Database.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(sql)
                return await cursor.fetchall()

    @staticmethod
    async def get_leaderboard(sort_by: str):

        sql = f'SELECT * FROM user_data ORDER BY {sort_by} DESC LIMIT 10;'

        async with Database.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(sql)
                data = await cursor.fetchall()

        lb = []

        for row in data:
            lb.append({'user': row['p_key'], 'value': row[sort_by]})

        return lb

    @staticmethod
    async def increment_value(table: str, column: str, primary_key: int):
        v: int = await Database.fetch(table, column, primary_key)  # use Database.fetch()
        await Database.update(table, column, primary_key, v + 1)  # use Database.update()
