"""MySQL 连接辅助（采集进程与 Flask 共用）"""
from contextlib import contextmanager
from typing import Any, Generator, Iterable, Optional

import pymysql
from pymysql.cursors import DictCursor

from collector import config


def get_connection():
    return pymysql.connect(
        host=config.MYSQL_HOST,
        port=config.MYSQL_PORT,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
    )


@contextmanager
def connection() -> Generator[pymysql.connections.Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_one(sql: str, args: Optional[Iterable[Any]] = None) -> Optional[dict]:
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, args or ())
            return cur.fetchone()


def fetch_all(sql: str, args: Optional[Iterable[Any]] = None) -> list:
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, args or ())
            return list(cur.fetchall())


def execute(sql: str, args: Optional[Iterable[Any]] = None) -> int:
    with connection() as conn:
        with conn.cursor() as cur:
            n = cur.execute(sql, args or ())
            return int(n)
