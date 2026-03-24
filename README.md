# Digital EDD Logger

SDK de logging para servicios Python con soporte para PostgreSQL (desarrollo) y Google Cloud PubSub (producción).

## Instalación.

```bash
pip install git+https://github.com/icastillogomar/digital-logger-edd-python.git
```

## Uso Rápido

```python
from digital_edd_logger import logger

logger.sendTraceByLog(
    log_id="bd24e7ad-2e41-4638-b129-c1dd7e125faa",
    request_id="bd24e7ad-2e41-4638-b129-c1dd7e125faa",
    request_type="HTTP",
    endpoint="/api/orders",
    log_at="2026-03-10 11:24:37.079000 UTC",
    id_txn="bd24e7ad-2e41-4638-b129-c1dd7e125faa",
    ingested_at="2026-03-10 11:24:37.079000 UTC",
    level="INFO",
    context="OrderService",
    message="HTTP request/response trace",
    step="RequestResponseLogger",
    duration_ms=150.5,
    tags= ["http", "middleware", "request-response"],
    extra={"clientIp":  "201.116.168.4", "userAgent": "PostmanRuntime/7.52.0"},
    service_name="my-service",
    request_method= "GET",    
    request_body={"product": "ABC", "qty": 2},
    status_code=200,
    response_body={"order_id": "12345"}
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

| ENV                               | Driver     | Destino                      |
|-----------------------------------|------------|------------------------------|
| `local` (o vacío)                 | PostgreSQL | Tabla `LGS_EDD_IA_LOGS_HIS`  |
| `prod`, `production`, `qa`, `qas` | PubSub     | Topic `digital-edd-sdk`      |

Si falta configuración, usa `ConsoleDriver` como fallback y muestra el error en consola.


## Variables de Entorno

| Variable               | Descripción                    | Requerido                             |
|------------------------|--------------------------------|---------------------------------------|
| `DB_URL`               | URL de PostgreSQL              | Solo en local                         |
| `ENV`                  | `local` para forzar PostgreSQL | Opcional                              |
| `GOOGLE_CLOUD_PROJECT` | Project ID de GCP              | Solo en prod                          |
| `SDKTRACKING_PUBLISH`  | `false` para deshabilitar      | Opcional                              |
| `PUBSUB_TOPIC_NAME`    | Nombre del topic               | Opcional (default: `digital-edd-sdk`) |
