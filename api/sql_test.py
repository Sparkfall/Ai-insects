import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    conn = psycopg2.connect(
        dbname='insect',
        user='postgres',
        password="admin",
        host='localhost',
        port='7890'
    )
    return conn

def execute_query(query, params=None):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(query, params)
    conn.commit()
    result = cursor.fetchall() if cursor.rowcount > 1 else cursor.fetchone()
    cursor.close()
    conn.close()
    return result

get_db_connection()