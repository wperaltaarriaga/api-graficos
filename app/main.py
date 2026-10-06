"""
API de solo lectura sobre Oracle para los gráficos del front.

Correr:  uvicorn app.main:app --reload
Docs:    http://localhost:8000/docs
"""
import logging
from contextlib import asynccontextmanager

import oracledb
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import charts, db
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        db.get_pool()
    except oracledb.Error as exc:
        # La app arranca igual; se reintenta conectar en el próximo request.
        logger.error("No se pudo conectar a Oracle: %s", exc)
    yield
    db.close_pool()


app = FastAPI(title="API de gráficos", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(charts.router)


@app.exception_handler(oracledb.Error)
def oracle_error(request: Request, exc: oracledb.Error):
    # El detalle (ORA-xxxxx) va al log, no al navegador.
    logger.exception("Error de Oracle en %s", request.url.path)
    return JSONResponse(status_code=503, content={"detail": "Error al consultar la base de datos"})


@app.get("/health", tags=["Estado"])
def health():
    db.fetch_all("SELECT 1 FROM DUAL")
    return {"status": "ok"}
