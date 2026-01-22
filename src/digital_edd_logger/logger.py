from typing import Any, Dict, List, Optional
from .interfaces import TraceLog, RequestInfo, ResponseInfo, LogLevel
from .drivers import BaseDriver, ConsoleDriver
from .utils import is_gcp_environment, get_mexico_time_as_utc, log_error, log_warning


class EddLogger:

    def __init__(self, service: str = "digital-edd"):
        self.service = service
        self._driver: Optional[BaseDriver] = None

    @property
    def driver(self) -> BaseDriver:
        if self._driver is None:
            self._driver = self._create_driver()
        return self._driver

    def _create_driver(self) -> BaseDriver:
        if is_gcp_environment():
            try:
                from .drivers import PubSubDriver
                return PubSubDriver()
            except Exception as e:
                log_error(f"No se pudo inicializar PubSubDriver: {e}")
                log_warning("Usando ConsoleDriver como fallback")
                return ConsoleDriver()
        else:
            try:
                from .drivers import PostgresDriver
                return PostgresDriver()
            except Exception as e:
                log_error(f"No se pudo inicializar PostgresDriver: {e}")
                log_warning("Usando ConsoleDriver como fallback")
                return ConsoleDriver()

    def set_driver(self, driver: BaseDriver) -> None:
        self._driver = driver

    def send_trace_log(self, trace: TraceLog) -> str:
        record = trace.to_dict()
        return self.driver.send(record)

    def log(
        self,
        *,
        trace_id: str,
        level: LogLevel = "INFO",
        action: str = "",
        context: Optional[str] = None,
        method: Optional[str] = None,
        path: Optional[str] = None,
        request_headers: Optional[Dict[str, str]] = None,
        request_body: Optional[Any] = None,
        status_code: Optional[int] = None,
        response_headers: Optional[Dict[str, str]] = None,
        response_body: Optional[Any] = None,
        message_info: Optional[str] = None,
        message_raw: Optional[str] = None,
        duration_ms: Optional[float] = None,
        tags: Optional[List[str]] = None,
        service: Optional[str] = None,
    ) -> str:
        request = None
        if method and path:
            request = RequestInfo(
                method=method,
                path=path,
                headers=request_headers,
                body=request_body,
            )

        response = None
        if status_code is not None:
            response = ResponseInfo(
                statusCode=status_code,
                headers=response_headers,
                body=response_body,
            )

        trace = TraceLog(
            traceId=trace_id,
            timestamp=get_mexico_time_as_utc(),
            service=service or self.service,
            level=level,
            action=action,
            context=context,
            request=request,
            response=response,
            messageInfo=message_info,
            messageRaw=message_raw,
            durationMs=duration_ms,
            tags=tags,
        )

        return self.send_trace_log(trace)
