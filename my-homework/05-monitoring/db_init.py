import os
import psycopg

def get_db_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        dbname=os.getenv("POSTGRES_DB", "course_assistant"),
        user=os.getenv("POSTGRES_USER", "user"),
        password=os.getenv("POSTGRES_PASSWORD", "password"),
    )

def init_db(drop=False):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if drop:
                cur.execute("DROP TABLE IF EXISTS spans")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS spans (
                    id SERIAL PRIMARY KEY,
                    span_name TEXT NOT NULL,
                    duration FLOAT NOT NULL,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Base de datos inicializada")
