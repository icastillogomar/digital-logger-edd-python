# Digital EDD Logger

SDK de logging para servicios Python con soporte para PostgreSQL (desarrollo) y Google Cloud PubSub (producción).

## Instalación

```bash
pip install git+https://github.com/icastillogomar/digital-logger-edd-python.git
```

## Uso Rápido

```python
from digital_edd_logger import logger

logger.log(
    trace_id="abc-123",
    action="ORDER_CREATED",
    context="OrderService",
    method="POST",
    path="/api/orders",
    request_body={"product": "ABC", "qty": 2},
    status_code=200,
    response_body={"order_id": "12345"},
    duration_ms=150.5,
)
```

## Configuración

### Local/Dev (PostgreSQL)

```bash
DB_URL=postgresql://user:password@localhost:5432/mydb
ENV=local
```

### Producción/QA (PubSub)

```bash
ENV=prod  # o "production", "qa", "qas"
GOOGLE_CLOUD_PROJECT=my-project-id
```

## Comportamiento

| ENV | Driver | Destino |
|-----|--------|---------|
| `local` (o vacío) | PostgreSQL | Tabla `LGS_EDD_SDK_HIS` |
| `prod`, `production`, `qa`, `qas` | PubSub | Topic `digital-edd-sdk` |

Si falta configuración, usa `ConsoleDriver` como fallback y muestra el error en consola.

## API

```python
logger.log(
    trace_id: str,              # ID único de la traza
    level: str = "INFO",        # DEBUG, INFO, WARNING, ERROR, CRITICAL
    action: str = "",           # Acción registrada
    context: str = None,        # Nombre del servicio/controller
    method: str = None,         # GET, POST, PUT, DELETE
    path: str = None,           # /api/endpoint
    request_body: any = None,   # Body del request
    status_code: int = None,    # 200, 400, 500, etc.
    response_body: any = None,  # Body de la respuesta
    duration_ms: float = None,  # Tiempo de ejecución
    message_info: str = None,   # Info adicional
    tags: list = None,          # Tags para filtrar
)
```

## Ejemplo con FastAPI

```python
from fastapi import FastAPI, Request
from digital_edd_logger import logger
import uuid
import time

app = FastAPI()

@app.post("/api/orders")
async def create_order(request: Request):
    trace_id = str(uuid.uuid4())
    start = time.time()
    
    body = await request.json()
    result = {"order_id": "12345"}
    
    logger.log(
        trace_id=trace_id,
        action="ORDER_CREATED",
        context="OrderController",
        method="POST",
        path="/api/orders",
        request_body=body,
        status_code=200,
        response_body=result,
        duration_ms=(time.time() - start) * 1000,
    )
    
    return result
```

## Variables de Entorno

| Variable | Descripción | Requerido |
|----------|-------------|-----------|
| `DB_URL` | URL de PostgreSQL | Solo en local |
| `ENV` | `local` para forzar PostgreSQL | Opcional |
| `GOOGLE_CLOUD_PROJECT` | Project ID de GCP | Solo en prod |
| `SDKTRACKING_PUBLISH` | `false` para deshabilitar | Opcional |
| `PUBSUB_TOPIC_NAME` | Nombre del topic | Opcional (default: `digital-edd-sdk`) |
