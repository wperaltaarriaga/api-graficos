"""
Endpoints que alimentan los gráficos del front.

Cada endpoint = una consulta SQL que ya devuelve los datos agrupados,
listos para pasarle al gráfico (por ejemplo, a Recharts en React).

Las consultas de abajo son EJEMPLOS sobre una tabla VENTAS(fecha, categoria, monto):
reemplazarlas por las tablas reales de la empresa.
Los valores que vienen del front siempre van como bind variables (:desde), nunca concatenados.
"""
from datetime import date
from typing import Optional

from fastapi import APIRouter

from app import db

router = APIRouter(prefix="/api/charts", tags=["Gráficos"])

# Filtro opcional por rango de fechas: si no se manda, no filtra.
FILTRO_FECHAS = "(:desde IS NULL OR fecha >= :desde) AND (:hasta IS NULL OR fecha < :hasta + 1)"


@router.get("/ventas-por-mes", summary="Línea / barras: total vendido por mes")
def ventas_por_mes(desde: Optional[date] = None, hasta: Optional[date] = None):
    return db.fetch_all(
        f"""
        SELECT TO_CHAR(TRUNC(fecha, 'MM'), 'YYYY-MM') AS mes,
               SUM(monto)                            AS total
        FROM ventas
        WHERE {FILTRO_FECHAS}
        GROUP BY TRUNC(fecha, 'MM')
        ORDER BY TRUNC(fecha, 'MM')
        """,
        {"desde": desde, "hasta": hasta},
    )


@router.get("/ventas-por-categoria", summary="Torta / barras: total vendido por categoría")
def ventas_por_categoria(desde: Optional[date] = None, hasta: Optional[date] = None):
    return db.fetch_all(
        f"""
        SELECT categoria,
               SUM(monto) AS total
        FROM ventas
        WHERE {FILTRO_FECHAS}
        GROUP BY categoria
        ORDER BY total DESC
        """,
        {"desde": desde, "hasta": hasta},
    )


@router.get("/resumen", summary="Tarjetas de indicadores (KPIs)")
def resumen(desde: Optional[date] = None, hasta: Optional[date] = None):
    rows = db.fetch_all(
        f"""
        SELECT COUNT(*)                  AS cantidad_ventas,
               NVL(SUM(monto), 0)        AS total_vendido,
               NVL(ROUND(AVG(monto), 2), 0) AS ticket_promedio
        FROM ventas
        WHERE {FILTRO_FECHAS}
        """,
        {"desde": desde, "hasta": hasta},
    )
    return rows[0]
