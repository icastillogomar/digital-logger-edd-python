# Digital EDD Logger

SDK de logging para servicios Python con soporte para PostgreSQL (desarrollo) y Google Cloud PubSub (producción).

## Tabla de Contenidos

- [Instalación](#instalación)
- [Comportamiento por Entorno](#comportamiento-por-entorno)
- [Configuración](#configuración)
- [Uso](#uso)
- [API Reference](#api-reference)
- [Estructura de la Tabla](#estructura-de-la-tabla)
- [Drivers Disponibles](#drivers-disponibles)
- [Manejo de Errores](#manejo-de-errores)
- [Ejemplos](#ejemplos)

## Instalación

### Desde PyPI

```bash
# Solo PostgreSQL (local/dev)
pip install digital-edd-logger[postgres]

# Solo PubSub (prod)
pip install digital-edd-logger[pubsub]

# Ambos drivers
pip install digital-edd-logger[all]
```

### Desde el repositorio

```bash
git clone <repo-url>
cd digital-logger-edd-python
pip install -e .[all]
```

## Comportamiento por Entorno

El SDK detecta automáticamente el entorno y selecciona el driver apropiado:

| Entorno | Detección | Driver | Destino |
|---------|-----------|--------|---------|
| Local/Dev | `ENV=local` o ausencia de variables GCP | `PostgresDriver` | Tabla `LGS_EDD_SDK_HIS` |
| GCP (GKE/Cloud Run) | Presencia de `GOOGLE_CLOUD_PROJECT`, `K_SERVICE`, `KUBERNETES_SERVICE_HOST` | `PubSubDriver` | Topic PubSub |

### Detección de entorno GCP

El SDK considera que está en GCP si detecta alguna de estas variables:
- `K_SERVICE` (Cloud Run)
- `GOOGLE_CLOUD_PROJECT`
- `GCP_PROJECT`
- `KUBERNETES_SERVICE_HOST` (GKE)

Y además `ENV` no está seteado como `local`.

## Configuración

### Local/Dev (PostgreSQL)

```bash
DB_URL=postgresql://user:password@host:port/database
ENV=local
```

Ejemplo:
```bash
DB_URL=postgresql://postgres:postgres@localhost:5432/mydb
ENV=local
```

### Producción (PubSub)

```bash
GOOGLE_CLOUD_PROJECT=my-project-id
```

Variables opcionales:
```bash
SDKTRACKING_PUBLISH=true          # default: true, poner false para deshabilitar
PUBSUB_TOPIC_NAME=my-custom-topic # default: digital-edd-sdk
```

En GKE, `GOOGLE_CLOUD_PROJECT` ya viene configurado automáticamente y usa Workload Identity para autenticación.

## Uso

### Importación básica

```python
from digital_edd_logger import logger

logger.log(
    trace_id="abc-123",
    action="REQUEST_RECEIVED",
    context="MyService",
)
```

### Crear instancia personalizada

```python
from digital_edd_logger import EddLogger

my_logger = EddLogger(service="my-custom-service")
```

### Usar driver específico

```python
from digital_edd_logger import EddLogger
from digital_edd_logger.drivers import ConsoleDriver, PostgresDriver

logger = EddLogger(service="my-service")

# Forzar ConsoleDriver (para testing)
logger.set_driver(ConsoleDriver())

# Forzar PostgresDriver con config manual
logger.set_driver(PostgresDriver(db_url="postgresql://user:pass@localhost:5432/mydb"))
```

## API Reference

### `logger.log()`

Método principal para registrar logs.

```python
logger.log(
    trace_id: str,                    # Requerido - ID único de la traza
    level: LogLevel = "INFO",         # DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL, ALERT
    action: str = "",                 # Acción que se está registrando
    context: str = None,              # Contexto (ej: nombre del servicio/controller)
    method: str = None,               # Método HTTP (GET, POST, etc.)
    path: str = None,                 # Path del endpoint
    request_headers: dict = None,     # Headers del request
    request_body: any = None,         # Body del request
    status_code: int = None,          # Código de respuesta HTTP
    response_headers: dict = None,    # Headers de la respuesta
    response_body: any = None,        # Body de la respuesta
    message_info: str = None,         # Información adicional
    message_raw: str = None,          # Mensaje raw (ej: error completo)
    duration_ms: float = None,        # Duración en milisegundos
    tags: list[str] = None,           # Tags para categorización
    service: str = None,              # Override del nombre del servicio
)
```

### `logger.send_trace_log()`

Envía un `TraceLog` completo directamente.

```python
from digital_edd_logger import TraceLog, RequestInfo, ResponseInfo

trace = TraceLog(
    traceId="abc-123",
    timestamp="2025-01-22T10:00:00.000Z",
    service="my-service",
    level="INFO",
    action="REQUEST_PROCESSED",
    context="MyController",
    request=RequestInfo(
        method="POST",
        path="/api/data",
        headers={"Content-Type": "application/json"},
        body={"key": "value"},
    ),
    response=ResponseInfo(
        statusCode=200,
        body={"result": "ok"},
    ),
    durationMs=150.5,
    messageInfo="Procesado correctamente",
    tags=["api", "production"],
)

logger.send_trace_log(trace)
```

## Estructura de la Tabla

La tabla `LGS_EDD_SDK_HIS` se crea automáticamente en PostgreSQL:

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | SERIAL | NO | Primary key |
| `traceId` | VARCHAR(255) | NO | ID único de la traza |
| `timeLocal` | TIMESTAMP | NO | Timestamp local |
| `timeUTC` | TIMESTAMP | NO | Timestamp UTC |
| `service` | VARCHAR(255) | NO | Nombre del servicio |
| `level` | VARCHAR(50) | NO | Nivel del log |
| `user` | VARCHAR(255) | SI | Usuario (opcional) |
| `action` | VARCHAR(255) | SI | Acción registrada |
| `context` | VARCHAR(255) | SI | Contexto |
| `request` | JSONB | SI | Request completo |
| `response` | JSONB | SI | Response completo |
| `durationMs` | FLOAT | SI | Duración en ms |
| `tags` | TEXT | SI | Tags separados por coma |
| `messageInfo` | TEXT | SI | Información adicional |
| `messageRaw` | TEXT | SI | Mensaje raw |
| `flagSummary` | INTEGER | NO | Flag para procesamiento (default: 0) |

Índices creados automáticamente:
- `idx_lgs_edd_sdk_his_trace_id` en `traceId`
- `idx_lgs_edd_sdk_his_time_utc` en `timeUTC`

## Drivers Disponibles

### PostgresDriver

Para desarrollo local. Inserta logs en tabla PostgreSQL.

```python
from digital_edd_logger.drivers import PostgresDriver

driver = PostgresDriver(db_url="postgresql://user:pass@localhost:5432/mydb")
```

### PubSubDriver

Para producción en GCP. Publica mensajes a PubSub.

```python
from digital_edd_logger.drivers import PubSubDriver

driver = PubSubDriver(project_id="my-project", topic_name="my-topic")
```

### ConsoleDriver

Para testing o como fallback. Imprime logs a consola en formato JSON.

```python
from digital_edd_logger.drivers import ConsoleDriver

driver = ConsoleDriver()
```

## Manejo de Errores

El SDK maneja errores de configuración de forma graceful:

1. Si falta `DB_URL` en local o `GOOGLE_CLOUD_PROJECT` en GCP, muestra un error descriptivo
2. Automáticamente usa `ConsoleDriver` como fallback para no interrumpir la aplicación
3. Los mensajes de error se muestran con colores en terminales compatibles

Ejemplo de salida cuando falta configuración:
```
[digital-edd-logger] ERROR: No se pudo inicializar PostgresDriver: DB_URL no está configurado. Formato: postgresql://user:password@host:port/database
[digital-edd-logger] WARNING: Usando ConsoleDriver como fallback
```

## Ejemplos

### FastAPI con middleware de logging

```python
from fastapi import FastAPI, Request
from digital_edd_logger import logger
import uuid
import time

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    start_time = time.time()
    
    response = await call_next(request)
    
    duration_ms = (time.time() - start_time) * 1000
    
    logger.log(
        trace_id=trace_id,
        action="HTTP_REQUEST",
        context="FastAPIMiddleware",
        method=request.method,
        path=str(request.url.path),
        status_code=response.status_code,
        duration_ms=duration_ms,
    )
    
    return response
```

### Logging de errores

```python
from digital_edd_logger import logger
import time

def process_order(order_id: str, trace_id: str):
    start_time = time.time()
    
    try:
        result = do_something()
        
        logger.log(
            trace_id=trace_id,
            action="ORDER_PROCESSED",
            context="OrderService",
            status_code=200,
            response_body={"order_id": order_id, "status": "completed"},
            duration_ms=(time.time() - start_time) * 1000,
        )
        
        return result
        
    except Exception as e:
        logger.log(
            trace_id=trace_id,
            level="ERROR",
            action="ORDER_FAILED",
            context="OrderService",
            status_code=500,
            message_raw=str(e),
            duration_ms=(time.time() - start_time) * 1000,
        )
        raise
```

### Cloud Function con PubSub

```python
import functions_framework
from digital_edd_logger import logger
import json

@functions_framework.cloud_event
def process_message(cloud_event):
    trace_id = cloud_event.get("id", "unknown")
    data = json.loads(cloud_event.data["message"]["data"])
    
    logger.log(
        trace_id=trace_id,
        action="PUBSUB_RECEIVED",
        context="CloudFunction",
        request_body=data,
        status_code=200,
    )
```

## Licencia

MIT
