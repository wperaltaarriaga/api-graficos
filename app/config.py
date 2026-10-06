"""Configuración: se lee de variables de entorno o del archivo .env."""
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Oracle
    ORACLE_USER: str = ""
    ORACLE_PASSWORD: str = ""
    ORACLE_DSN: str = "localhost:1521/SERVICIO"  # host:puerto/service_name
    ORACLE_POOL_MAX: int = 4
    # Solo si la base es anterior a Oracle 12.1: ruta al Instant Client
    ORACLE_CLIENT_LIB_DIR: Optional[str] = None

    # URLs del front React, separadas por coma
    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
