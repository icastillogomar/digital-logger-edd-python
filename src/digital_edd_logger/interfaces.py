from dataclasses import MISSING, dataclass, fields, is_dataclass
from typing import Any, Dict, List, Literal, Optional

LogLevel = Literal["DEBUG", "INFO", "NOTICE", "WARNING", "ERROR", "CRITICAL", "ALERT"]


def _serialize_value(value: Any) -> Any:
    if is_dataclass(value):
        return _serialize_dataclass(value)
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize_value(item) for key, item in value.items()}
    return value


def _should_omit_optional(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def _serialize_dataclass(instance: Any) -> Dict[str, Any]:
    result: Dict[str, Any] = {}

    for field_info in fields(instance):
        value = getattr(instance, field_info.name)
        required = (
            field_info.default is MISSING and
            field_info.default_factory is MISSING
        )

        if not required and _should_omit_optional(value):
            continue

        result[field_info.name] = _serialize_value(value)

    return result


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
        return _serialize_dataclass(self)


@dataclass
class EddLine:
    sku: str
    quantity: int
    productType: str


@dataclass
class RecalculateLine:
    sku: str
    purchaseDateEdd1: str
    deliveryDateEdd2: str
    quantity: Optional[int] = None
    storeRejected: Optional[str] = None
    carrierRejected: Optional[str] = None


@dataclass
class TraceByInput:
    typeStream: str
    requestId: str
    requestType: str
    endpoint: str
    receivedAt: str
    enterpriseCode: str
    cp: str
    channel: str
    ingestedAt: str
    eddLines: Optional[EddLine] = None
    recalculateLines: Optional[RecalculateLine] = None
    lineCount: Optional[int] = None
    tags: Optional[List[str]] = None
    additionalData: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return _serialize_dataclass(self)


@dataclass
class OutputMetadata:
    idTxn: Optional[str] = None
    processingTimeMs: Optional[int] = None
    ingestedAt: Optional[str] = None
    recalculateOrder: Optional[str] = None


@dataclass
class AlgorithmWeights:
    inventory: Optional[float] = None
    leadTime: Optional[float] = None
    cost: Optional[float] = None
    node: Optional[float] = None
    path: Optional[float] = None
    difference: Optional[float] = None
    splits: Optional[float] = None


@dataclass
class EddCalculatedSummary:
    split: Optional[bool] = None
    productType: Optional[str] = None
    maxDeliveryDays: Optional[int] = None
    usedRoutes: Optional[int] = None
    storeSelected: Optional[str] = None
    storeName: Optional[str] = None
    edd1: Optional[str] = None
    totalCost: Optional[float] = None
    plan: Optional[str] = None
    errorCode: Optional[str] = None
    errorMessage: Optional[str] = None


@dataclass
class EddCalculatedRoute:
    idRoute: Optional[str] = None
    quantity: Optional[int] = None
    deliveryDate: Optional[str] = None
    timeDays: Optional[int] = None
    cost: Optional[float] = None
    deliveryMethod: Optional[str] = None
    idCarrier: Optional[int] = None
    storeId: Optional[int] = None
    storeName: Optional[str] = None
    storeCapacity: Optional[int] = None
    inventory: Optional[int] = None
    availableStores: Optional[int] = None


@dataclass
class EddCalculated:
    sku: str
    summary: List[EddCalculatedSummary]
    routes: List[EddCalculatedRoute]


@dataclass
class TraceByOutput:
    typeStream: str
    requestId: str
    requestType: str
    endpoint: str
    respondedAt: str
    httpStatusCode: int
    ingestedAt: str
    statusFamily: Optional[int] = None
    isError: Optional[bool] = None
    metadata: Optional[OutputMetadata] = None
    algorithmModelState: Optional[str] = None
    algorithmWeights: Optional[AlgorithmWeights] = None
    eddCalculated: Optional[EddCalculated] = None
    storeIds: Optional[List[int]] = None
    errorCode: Optional[str] = None
    errorMessage: Optional[str] = None
    tags: Optional[List[str]] = None
    additionalData: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return _serialize_dataclass(self)


@dataclass
class LogRequestPayload:
    method: str
    body: Optional[Any] = None


@dataclass
class LogResponsePayload:
    statusCode: int
    body: Optional[Any] = None


@dataclass
class TraceByLog:
    typeStream: str
    logId: str
    requestId: str
    requestType: str
    endpoint: str
    logAt: str
    idTxn: str
    ingestedAt: str
    level: Optional[str] = None
    context: Optional[str] = None
    message: Optional[str] = None
    step: Optional[str] = None
    durationMs: Optional[float] = None
    tags: Optional[List[str]] = None
    additionalData: Optional[Any] = None
    extra: Optional[Any] = None
    stacktrace: Optional[str] = None
    serviceName: Optional[str] = None
    request: Optional[LogRequestPayload] = None
    response: Optional[LogResponsePayload] = None

    def to_dict(self) -> Dict[str, Any]:
        return _serialize_dataclass(self)
