from typing import Any, Dict, List, Optional, Literal
from dataclasses import dataclass

LogLevel = Literal["DEBUG", "INFO", "NOTICE", "WARNING", "ERROR", "CRITICAL", "ALERT"]


@dataclass
class RequestInfo:
    method: str
    path: str
    headers: Optional[Dict[str, str]] = None
    body: Optional[Any] = None


@dataclass
class ResponseInfo:
    statusCode: int
    headers: Optional[Dict[str, str]] = None
    body: Optional[Any] = None


@dataclass
class TraceLog:
    traceId: str
    timestamp: str
    service: str
    level: LogLevel
    action: str
    context: Optional[str] = None
    request: Optional[RequestInfo] = None
    response: Optional[ResponseInfo] = None
    messageInfo: Optional[str] = None
    messageRaw: Optional[str] = None
    durationMs: Optional[float] = None
    tags: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "traceId": self.traceId,
            "timestamp": self.timestamp,
            "service": self.service,
            "level": self.level,
            "action": self.action,
        }
        if self.context:
            result["context"] = self.context
        if self.request:
            result["request"] = {
                "method": self.request.method,
                "path": self.request.path,
            }
            if self.request.headers:
                result["request"]["headers"] = self.request.headers
            if self.request.body is not None:
                result["request"]["body"] = self.request.body
        if self.response:
            result["response"] = {"statusCode": self.response.statusCode}
            if self.response.headers:
                result["response"]["headers"] = self.response.headers
            if self.response.body is not None:
                result["response"]["body"] = self.response.body
        if self.messageInfo:
            result["messageInfo"] = self.messageInfo
        if self.messageRaw:
            result["messageRaw"] = self.messageRaw
        if self.durationMs is not None:
            result["durationMs"] = self.durationMs
        if self.tags:
            result["tags"] = self.tags
        return result
