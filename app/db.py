"""Conexión a Oracle: un pool de conexiones compartido por toda la app."""
from typing import Any, Dict, List, Optional

import oracledb

from app.config import settings

_pool: Optional[oracledb.ConnectionPool] = None


def get_pool() -> oracledb.ConnectionPool:
    global _pool
    if _pool is None:
        if settings.ORACLE_CLIENT_LIB_DIR:
            oracledb.init_oracle_client(lib_dir=settings.ORACLE_CLIENT_LIB_DIR)
        _pool = oracledb.create_pool(
            user=settings.ORACLE_USER,
            password=settings.ORACLE_PASSWORD,
            dsn=settings.ORACLE_DSN,
            min=1,
            max=settings.ORACLE_POOL_MAX,
        )
    return _pool


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close(force=True)
        _pool = None


def fetch_all(sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Ejecuta un SELECT y devuelve una lista de dicts: [{"columna": valor, ...}, ...]"""
    with get_pool().acquire() as conn, conn.cursor() as cur:
        cur.execute(sql, params or {})
        columns = [col[0].lower() for col in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]
