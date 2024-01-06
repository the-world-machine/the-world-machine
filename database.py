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
    
    @staticmethod
    async def get_pool():
        
        if Database.pool is None:
            await Database.create_pool()
            
        return Database.pool

    @listen(Startup)
    async def on_ready(self):
        await Database.create_pool()

    @staticmethod
    async def execute(sql: str, *values: any) -> aiomysql.Cursor or None:
        
        get_pool = await Database.get_pool()

        async with get_pool.acquire() as conn:
            async with conn.cursor(aiomysql.Cursor) as cursor:
                await cursor.execute(sql, values)

        return cursor

    @staticmethod
    async def fetch(table: str, primary_key: Union[int, Snowflake], what: str = None) -> any:
        if type(primary_key) == Snowflake:
            primary_key = int(primary_key)

        select_sql = f"SELECT * FROM {table} WHERE p_key = {primary_key}"
            
        column_sql = f"DESCRIBE {table}"
        
        cursor = await Database.execute(select_sql)
        row = await cursor.fetchone()
        
        if not row:
            await Database.new_entry(table, primary_key)  # use Database.new_entry()
            return await Database.fetch(table, primary_key, what)  # use Database.fetch()

        cursor = await Database.execute(column_sql)
        column_data = await cursor.fetchall()
                
        result_dict = {}
                
        for i in range(len(column_data)):
            column = column_data[i]
            
            key = column[0]
            dtype = column[1]
            value = row[i]
            
            if dtype == 'longtext' and value != 'NULL':
                value = json.loads(value)
                
            if value == 'NULL':
                value = None
            
            result_dict[key] = value
            
        if not what:
            return result_dict
        else:
            return result_dict[what]

    @staticmethod
    async def new_entry(table: str, primary_key: int):
        insert_sql = f'INSERT INTO `{table}` (p_key) VALUES ({primary_key})'
        await Database.execute(insert_sql)

    @staticmethod
    async def update(table: str, column: str, p_key: Union[int, Snowflake] = None, data = None):
        if p_key is None:
            raise ValueError("Primary key is not set.")
        
        elif data is None:
            data = 'NULL'

        if type(p_key) == Snowflake:
            p_key = int(p_key)
            
        if type(data) == dict or type(data) == list or type(data) == bool:
            data = json.dumps(data)

        # Check if the primary key already exists in the table
        select_sql = f"SELECT * FROM `{table}` WHERE p_key = %s"
        cursor = await Database.execute(select_sql, p_key)

        row = await cursor.fetchone()

        if row:
            update_sql = f"UPDATE `{table}` SET `{column}` = %s WHERE p_key = %s"
            await Database.execute(update_sql, data, p_key)
        else:
            insert_sql = f"INSERT INTO `{table}` (p_key, `{column}`) VALUES (%s, %s)"
            await Database.execute(insert_sql, p_key, data)

    @staticmethod
    async def get_leaderboard(sort_by: str):

        sql = f'SELECT * FROM user_data ORDER BY {sort_by} DESC LIMIT 10;'
    
        cursor = await Database.execute(sql)
        data = await cursor.fetchall()

        lb = []

        for row in data:
            lb.append({'user': row['p_key'], 'value': row[sort_by]})

        return lb

    @staticmethod
    async def increment_value(table: str, column: str, primary_key: int, amount = 1):
        v: int = await Database.fetch(table, primary_key, column)  # use Database.fetch()
        await Database.update(table, column, primary_key, v + amount)  # use Database.update()
    
    @staticmethod
    async def update_table(table: str, p_key: int, data_: dict, **what: str):
        
        if not what:
            for key in data_:
                await Database.update(table, key, p_key, data_[key])
        else:
            for key, value in what.items():
                await Database.update(table, key, p_key, value)
                
        return data_
    
    @staticmethod
    async def fetch_shop_data():
        
        data = await Database.fetch('ShopData', 0)
        
        return data