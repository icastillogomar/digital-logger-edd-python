from .logger import EddLogger
from .interfaces import TraceLog, LogLevel, RequestInfo, ResponseInfo

logger = EddLogger()

__all__ = ["logger", "EddLogger", "TraceLog", "LogLevel", "RequestInfo", "ResponseInfo"]
__version__ = "1.0.0"
