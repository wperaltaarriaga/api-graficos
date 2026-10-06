"""Tests sin Oracle: se reemplaza db.fetch_all por una función falsa."""
import oracledb
from fastapi.testclient import TestClient

from app import db
from app.main import app

client = TestClient(app)  # sin "with": no ejecuta el lifespan, no intenta conectar


def test_ventas_por_mes(monkeypatch):
    calls = []

    def fake_fetch_all(sql, params=None):
        calls.append(params)
        return [{"mes": "2026-01", "total": 1500}, {"mes": "2026-02", "total": 2300}]

    monkeypatch.setattr(db, "fetch_all", fake_fetch_all)

    res = client.get("/api/charts/ventas-por-mes", params={"desde": "2026-01-01"})

    assert res.status_code == 200
    assert res.json() == [{"mes": "2026-01", "total": 1500}, {"mes": "2026-02", "total": 2300}]
    assert str(calls[0]["desde"]) == "2026-01-01"
    assert calls[0]["hasta"] is None


def test_resumen(monkeypatch):
    monkeypatch.setattr(db, "fetch_all", lambda sql, params=None: [
        {"cantidad_ventas": 2, "total_vendido": 3800, "ticket_promedio": 1900}
    ])
    res = client.get("/api/charts/resumen")
    assert res.status_code == 200
    assert res.json()["total_vendido"] == 3800


def test_fecha_invalida_422():
    res = client.get("/api/charts/ventas-por-mes", params={"desde": "no-es-fecha"})
    assert res.status_code == 422


def test_error_de_oracle_503(monkeypatch):
    def broken(sql, params=None):
        raise oracledb.DatabaseError("ORA-00942: table or view does not exist")

    monkeypatch.setattr(db, "fetch_all", broken)
    res = client.get("/api/charts/ventas-por-categoria")
    assert res.status_code == 503
    assert "ORA-" not in res.text  # el error interno no se filtra al front
