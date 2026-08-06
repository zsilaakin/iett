from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.getenv("CLICKHOUSE_HOST")
PORT = int(os.getenv("CLICKHOUSE_PORT"))
USER = os.getenv("CLICKHOUSE_USER")
PASSWORD = os.getenv("CLICKHOUSE_PASSWORD")
DATABASE = os.getenv("CLICKHOUSE_DATABASE")