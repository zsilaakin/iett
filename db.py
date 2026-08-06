import clickhouse_connect

from config import HOST, PORT, USER, PASSWORD, DATABASE

client = clickhouse_connect.get_client(
    host=HOST,
    port=PORT,
    username=USER,
    password=PASSWORD,
    database=DATABASE
)