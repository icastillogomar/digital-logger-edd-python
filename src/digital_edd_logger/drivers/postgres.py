import os
from .base import BaseDriver
from ..utils import log_info


class PostgresDriver(BaseDriver):

    TABLE_NAME = "LGS_EDD_SDK_HIS"

    DDL = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id SERIAL PRIMARY KEY,
        traceId VARCHAR(255) NOT NULL,
        timeLocal TIMESTAMP NOT NULL,
        timeUTC TIMESTAMP NOT NULL,
        service VARCHAR(255) NOT NULL,
        level VARCHAR(50) NOT NULL,
        "user" VARCHAR(255),
        action VARCHAR(255),
        context VARCHAR(255),
        request JSONB,
        response JSONB,
        durationMs FLOAT,
        tags TEXT,
        messageInfo TEXT,
        messageRaw TEXT,
        flagSummary INTEGER NOT NULL DEFAULT 0
    );
    CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME.lower()}_trace_id ON {TABLE_NAME}(traceId);
    CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME.lower()}_time_utc ON {TABLE_NAME}(timeUTC);
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

        import json
        from datetime import datetime

        sql = f"""
        INSERT INTO {self.TABLE_NAME} 
            (traceId, timeLocal, timeUTC, service, level, "user", action, context, 
             request, response, durationMs, tags, messageInfo, messageRaw, flagSummary)
        VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """

        now = datetime.now()
        now_utc = datetime.utcnow()

        request_json = json.dumps(record.get("request"), ensure_ascii=False) if record.get("request") else None
        response_json = json.dumps(record.get("response"), ensure_ascii=False) if record.get("response") else None
        tags_str = ",".join(record.get("tags", [])) if record.get("tags") else None

        values = (
            record.get("traceId"),
            now,
            now_utc,
            record.get("service"),
            record.get("level"),
            record.get("user"),
            record.get("action"),
            record.get("context"),
            request_json,
            response_json,
            record.get("durationMs"),
            tags_str,
            record.get("messageInfo"),
            record.get("messageRaw"),
            0,
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
