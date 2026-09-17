import os
import psycopg2
from dotenv import load_dotenv

from app.database.connect import CONN_PARAMS

load_dotenv()

QUERY_TIMEOUT_SECONDS = int(int(os.getenv('QUERY_TIMEOUT_SECONDS')) * 1000)
QUERY_ROW_LIMIT = int(os.getenv('QUERY_ROW_LIMIT'))

def execute_sql(sql: str) -> tuple[list[dict] | None, str | None]:
    try:
        conn = psycopg2.connect(**CONN_PARAMS)
        conn.set_session(readonly=True)
        
        with conn.cursor() as cur:
            cur.execute(f"SET statement_timeout = {QUERY_TIMEOUT_SECONDS}")
            cur.execute(sql)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchmany(QUERY_ROW_LIMIT)
            result = [dict(zip(columns, row)) for row in rows]

        conn.close()
        return result, None
    
    except Exception as e:
        return None, str(e)