from .logger import EddLogger
from .interfaces import (
    AlgorithmWeights,
    EddCalculated,
    EddCalculatedRoute,
    EddCalculatedSummary,
    EddLine,
    LogLevel,
    LogRequestPayload,
    LogResponsePayload,
    OutputMetadata,
    RecalculateLine,
    RequestInfo,
    ResponseInfo,
    TraceByInput,
    TraceByLog,
    TraceByOutput,
    TraceLog,
)

logger = EddLogger()

__all__ = [
    "logger",
    "EddLogger",
    "TraceLog",
    "TraceByInput",
    "TraceByOutput",
    "TraceByLog",
    "LogLevel",
    "RequestInfo",
    "ResponseInfo",
    "EddLine",
    "RecalculateLine",
    "OutputMetadata",
    "AlgorithmWeights",
    "EddCalculatedSummary",
    "EddCalculatedRoute",
    "EddCalculated",
    "LogRequestPayload",
    "LogResponsePayload",
]
__version__ = "1.0.0"
