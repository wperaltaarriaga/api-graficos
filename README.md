# API de gráficos (Python + Oracle)

API de **solo lectura**: consulta tablas de Oracle y devuelve los datos ya agrupados para que el front en React arme los gráficos.
Se despliega en un servidor de la empresa y solo es accesible por VPN, por eso no tiene login.

```
React (gráficos)  --GET-->  FastAPI  --SELECT-->  Oracle
```

## Archivos

```
backend-python/
├── app/
│   ├── main.py      # crea la app: CORS, manejo de errores de Oracle, /health
│   ├── config.py    # lee el .env
│   ├── db.py        # pool de conexiones + fetch_all(sql, params)
│   └── charts.py    # un endpoint por gráfico, cada uno con su SELECT
├── tests/test_charts.py
├── .env.example
├── requirements.txt / requirements-dev.txt
└── Dockerfile
```

## Correrlo

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env        # completar con los datos de Oracle
uvicorn app.main:app --reload
```

- Documentación y prueba de endpoints: http://localhost:8000/docs
- Verificar la conexión a Oracle: http://localhost:8000/health
- Tests (no necesitan Oracle): `pytest`

## Datos que hay que pedirle al DBA

- Host, puerto y **SERVICE_NAME**. Con eso se arma `ORACLE_DSN=host:1521/SERVICE_NAME`.
- Un usuario con permiso **solo de SELECT** sobre las tablas que se van a leer.
- La versión de Oracle. Desde la 12.1 funciona sin instalar nada. Si es anterior, hay que instalar Oracle Instant Client y completar `ORACLE_CLIENT_LIB_DIR`.

## Agregar un gráfico

Las consultas de `charts.py` son **ejemplos** sobre una tabla `VENTAS(fecha, categoria, monto)`. Hay que reemplazarlas por las tablas reales.

Para sumar un gráfico se agrega una función en `app/charts.py`:

```python
@router.get("/clientes-por-zona")
def clientes_por_zona():
    return db.fetch_all("""
        SELECT zona, COUNT(*) AS cantidad
        FROM esquema.clientes
        GROUP BY zona
        ORDER BY cantidad DESC
    """)
```

Reglas:
- **Agrupar en el SQL** (`GROUP BY`, `SUM`, `COUNT`), no en Python. Al front le llegan pocas filas, ya listas para el gráfico.
- **Los valores que vienen del front van como bind variables** (`:desde`), nunca concatenados en el string. Así se evita la inyección SQL.
- Si las tablas son de otro esquema, se escribe el nombre completo: `ESQUEMA.TABLA`.

## Usarlo desde React (ejemplo con Recharts)

```jsx
import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip } from "recharts";

const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export function VentasPorMes() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch(`${API}/api/charts/ventas-por-mes?desde=2026-01-01`)
      .then((res) => res.json())
      .then(setData);
  }, []);

  // data = [{ mes: "2026-01", total: 1500 }, ...]
  return (
    <LineChart width={600} height={300} data={data}>
      <XAxis dataKey="mes" />
      <YAxis />
      <Tooltip />
      <Line dataKey="total" />
    </LineChart>
  );
}
```

`CORS_ORIGINS` en el `.env` tiene que incluir la URL donde corre el front.

## Errores

Cuando Oracle falla, la API responde `503 {"detail": "Error al consultar la base de datos"}`. El detalle (`ORA-xxxxx`) queda solo en el log del servidor.
