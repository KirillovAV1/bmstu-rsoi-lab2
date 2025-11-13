import os
import psycopg2
from contextlib import contextmanager

DB_DSN = os.getenv("DB_DSN", "postgresql://program:test@postgres:5432/reservations")


@contextmanager
def get_conn():
    conn = psycopg2.connect(DB_DSN)
    try:
        yield conn
    finally:
        conn.close()
