import os
from .base import BaseDriver
from ..utils import log_info


class PostgresDriver(BaseDriver):

    TABLE_NAME = "LGS_EDD_IA_LOGS_HIS"

    DDL = f"""
    CREATE TABLE IF NOT EXISTS LGS_EDD_IA_LOGS_HIS (
		id SERIAL PRIMARY KEY,
		logId VARCHAR(255),
		requestId VARCHAR(255),
		requestType VARCHAR(255),
		endpoint TEXT,
		logAt TIMESTAMP NOT NULL,
		level VARCHAR(50),
		context TEXT,
		message TEXT,
		step VARCHAR(255),
		durationMs DOUBLE PRECISION,
		idTxn VARCHAR(255),
		tags TEXT,
		additionalData JSONB,
		extra JSONB,
		stacktrace TEXT,
		ingestedAt TIMESTAMP NOT NULL,
		serviceName VARCHAR(255),
		requestMethod VARCHAR(50),
		requestBody JSONB,
		responseStatusCode INTEGER,
		responseBody JSONB
	);
	CREATE INDEX IF NOT EXISTS idx_lgs_edd_ia_logs_his_request_id ON LGS_EDD_IA_LOGS_HIS(requestId);
	CREATE INDEX IF NOT EXISTS idx_lgs_edd_ia_logs_his_log_at ON LGS_EDD_IA_LOGS_HIS(logAt);	
    """

    def __init__(self, db_url: str = None):
        self._db_url = db_url or os.getenv("DB_URL")
        self._conn = None
        self._migrated = False

        if not self._db_url:
            raise ValueError(
                "DB_URL no está configurado. Formato: postgresql://user:password@host:port/database"
            )

    def _ensure_connection(self):
        if self._conn is not None:
            return

        try:
            import psycopg2
        except ImportError:
            raise ImportError(
                "psycopg2 no está instalado. Ejecuta: pip install psycopg2-binary"
            )

        self._conn = psycopg2.connect(self._db_url)
        log_info("Conectado a PostgreSQL")

    def _ensure_table(self):
        if self._migrated:
            return

        self._ensure_connection()
        with self._conn.cursor() as cur:
            cur.execute(self.DDL)
        self._conn.commit()
        self._migrated = True
        log_info(f"Tabla {self.TABLE_NAME} verificada/creada")

    def send(self, record: dict) -> str:
        self._ensure_table()

        from datetime import datetime

        sql = f"""
        INSERT INTO {self.TABLE_NAME} 
            (logId, requestId, requestType, endpoint, logAt, level, context, message,
             step, durationMs, idTxn, tags, additionalData, extra, stacktrace,
             ingestedAt, serviceName, requestMethod, requestBody, responseStatusCode,
             responseBody)
        VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """

        def _parse_timestamp(value):
            if value is None:
                return None
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                normalized = value.replace("Z", "+00:00")
                try:
                    return datetime.fromisoformat(normalized)
                except ValueError:
                    return value
            return value

        now = datetime.utcnow()
        request = record.get("request") or {}
        response = record.get("response") or {}
        tags_str = ",".join(record.get("tags", [])) if record.get("tags") else None

        values = (
            record.get("logId") or record.get("traceId"),
            record.get("requestId") or record.get("traceId"),
            record.get("requestType"),
            record.get("endpoint") or request.get("path"),
            _parse_timestamp(
                record.get("logAt") or
                record.get("timestamp") or
                record.get("receivedAt") or
                record.get("respondedAt") or
                now
            ),
            record.get("level"),
            record.get("context"),
            record.get("message") or record.get("messageInfo") or record.get("messageRaw"),
            record.get("step") or record.get("action"),
            record.get("durationMs"),
            record.get("idTxn") or (record.get("metadata") or {}).get("idTxn"),
            tags_str,
            record.get("additionalData"),
            record.get("extra"),
            record.get("stacktrace"),
            _parse_timestamp(record.get("ingestedAt") or (record.get("metadata") or {}).get("ingestedAt") or now),
            record.get("serviceName") or record.get("service"),
            request.get("method"),
            request.get("body"),
            response.get("statusCode"),
            response.get("body"),
        )

        with self._conn.cursor() as cur:
            cur.execute(sql, values)
            row_id = cur.fetchone()[0]
        self._conn.commit()
        return str(row_id)

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
