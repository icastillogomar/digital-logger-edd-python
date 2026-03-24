from typing import Any, Dict, List, Optional
from .interfaces import (
    AlgorithmWeights,
    EddLine,
    EddCalculated,
    EddCalculatedRoute,
    EddCalculatedSummary,
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
from .drivers import BaseDriver, ConsoleDriver
from .utils import is_production, get_mexico_time_as_utc, log_error, log_warning, log_info


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
        if is_production():
            from .drivers import PubSubDriver
            return PubSubDriver()
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
        log_info(f"Se envio trama Log")
        record = trace.to_dict()
        return self.driver.send(record)

    def sendTraceByLog(
        self,
        *,
        log_id: str,
        request_id: str,
        request_type: str,
        endpoint: str,
        log_at: str,
        id_txn: str,
        ingested_at: str,
        level: Optional[str] = None,
        context: Optional[str] = None,
        message: Optional[str] = None,
        step: Optional[str] = None,
        duration_ms: Optional[float] = None,
        tags: Optional[List[str]] = None,
        additional_data: Optional[Any] = None,
        extra: Optional[Any] = None,
        stacktrace: Optional[str] = None,
        service_name: Optional[str] = None,
        request_method: Optional[str] = None,
        request_body: Optional[Any] = None,
        response_status_code: Optional[int] = None,
        response_body: Optional[Any] = None,
    ) -> str:
        request = None
        if request_method:
            request = LogRequestPayload(
                method=request_method,
                body=request_body,
            )

        response = None
        if response_status_code is not None:
            response = LogResponsePayload(
                statusCode=response_status_code,
                body=response_body,
            )

        trace = TraceByLog(
            typeStream="logsStream",
            logId=log_id,
            requestId=request_id,
            requestType=request_type,
            endpoint=endpoint,
            logAt=log_at,
            idTxn=id_txn,
            ingestedAt=ingested_at,
            level=level,
            context=context,
            message=message,
            step=step,
            durationMs=duration_ms,
            tags=tags,
            additionalData=additional_data,
            extra=extra,
            stacktrace=stacktrace,
            serviceName=service_name,
            request=request,
            response=response,
        )

        log_info("Se envio trama TraceByLog")
        return self.driver.send(trace.to_dict())

    def sendTraceByInput(
        self,
        *,
        request_id: str,
        request_type: str,
        endpoint: str,
        received_at: str,
        enterprise_code: str,
        cp: str,
        channel: str,
        ingested_at: str,
        edd_line_sku: Optional[str] = None,
        edd_line_quantity: Optional[int] = None,
        edd_line_product_type: Optional[str] = None,
        recalculate_line_sku: Optional[str] = None,
        recalculate_line_purchase_date_edd1: Optional[str] = None,
        recalculate_line_delivery_date_edd2: Optional[str] = None,
        recalculate_line_quantity: Optional[int] = None,
        recalculate_line_store_rejected: Optional[str] = None,
        recalculate_line_carrier_rejected: Optional[str] = None,
        line_count: Optional[int] = None,
        tags: Optional[List[str]] = None,
        additional_data: Optional[Any] = None,
    ) -> str:
        edd_lines = None
        if all(
            value is not None
            for value in (
                edd_line_sku,
                edd_line_quantity,
                edd_line_product_type,
            )
        ):
            edd_lines = EddLine(
                sku=edd_line_sku,
                quantity=edd_line_quantity,
                productType=edd_line_product_type,
            )

        recalculate_lines = None
        if all(
            value is not None
            for value in (
                recalculate_line_sku,
                recalculate_line_purchase_date_edd1,
                recalculate_line_delivery_date_edd2,
            )
        ):
            recalculate_lines = RecalculateLine(
                sku=recalculate_line_sku,
                purchaseDateEdd1=recalculate_line_purchase_date_edd1,
                deliveryDateEdd2=recalculate_line_delivery_date_edd2,
                quantity=recalculate_line_quantity,
                storeRejected=recalculate_line_store_rejected,
                carrierRejected=recalculate_line_carrier_rejected,
            )

        trace = TraceByInput(
            typeStream="inputStream",
            requestId=request_id,
            requestType=request_type,
            endpoint=endpoint,
            receivedAt=received_at,
            enterpriseCode=enterprise_code,
            cp=cp,
            channel=channel,
            ingestedAt=ingested_at,
            eddLines=edd_lines,
            recalculateLines=recalculate_lines,
            lineCount=line_count,
            tags=tags,
            additionalData=additional_data,
        )

        log_info("Se envio trama TraceByInput")
        return self.driver.send(trace.to_dict())

    def sendTraceByOutput(
        self,
        *,
        request_id: str,
        request_type: str,
        endpoint: str,
        responded_at: str,
        http_status_code: int,
        ingested_at: str,
        status_family: Optional[int] = None,
        is_error: Optional[bool] = None,
        metadata_id_txn: Optional[str] = None,
        metadata_processing_time_ms: Optional[int] = None,
        metadata_ingested_at: Optional[str] = None,
        metadata_recalculate_order: Optional[str] = None,
        algorithm_model_state: Optional[str] = None,
        algorithm_weights_inventory: Optional[float] = None,
        algorithm_weights_lead_time: Optional[float] = None,
        algorithm_weights_cost: Optional[float] = None,
        algorithm_weights_node: Optional[float] = None,
        algorithm_weights_path: Optional[float] = None,
        algorithm_weights_difference: Optional[float] = None,
        algorithm_weights_splits: Optional[float] = None,
        edd_calculated_sku: Optional[str] = None,
        edd_calculated_summary: Optional[List[Dict[str, Any]]] = None,
        edd_calculated_routes: Optional[List[Dict[str, Any]]] = None,
        store_ids: Optional[List[int]] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        tags: Optional[List[str]] = None,
        additional_data: Optional[Any] = None,
    ) -> str:
        metadata = None
        if any(
            value is not None
            for value in (
                metadata_id_txn,
                metadata_processing_time_ms,
                metadata_ingested_at,
                metadata_recalculate_order,
            )
        ):
            metadata = OutputMetadata(
                idTxn=metadata_id_txn,
                processingTimeMs=metadata_processing_time_ms,
                ingestedAt=metadata_ingested_at,
                recalculateOrder=metadata_recalculate_order,
            )

        algorithm_weights = None
        if any(
            value is not None
            for value in (
                algorithm_weights_inventory,
                algorithm_weights_lead_time,
                algorithm_weights_cost,
                algorithm_weights_node,
                algorithm_weights_path,
                algorithm_weights_difference,
                algorithm_weights_splits,
            )
        ):
            algorithm_weights = AlgorithmWeights(
                inventory=algorithm_weights_inventory,
                leadTime=algorithm_weights_lead_time,
                cost=algorithm_weights_cost,
                node=algorithm_weights_node,
                path=algorithm_weights_path,
                difference=algorithm_weights_difference,
                splits=algorithm_weights_splits,
            )

        edd_calculated = None
        if edd_calculated_sku:
            summaries = [
                EddCalculatedSummary(**summary)
                for summary in (edd_calculated_summary or [])
            ]
            routes = [
                EddCalculatedRoute(**route)
                for route in (edd_calculated_routes or [])
            ]
            edd_calculated = EddCalculated(
                sku=edd_calculated_sku,
                summary=summaries,
                routes=routes,
            )

        trace = TraceByOutput(
            typeStream="outputStream",
            requestId=request_id,
            requestType=request_type,
            endpoint=endpoint,
            respondedAt=responded_at,
            httpStatusCode=http_status_code,
            ingestedAt=ingested_at,
            statusFamily=status_family,
            isError=is_error,
            metadata=metadata,
            algorithmModelState=algorithm_model_state,
            algorithmWeights=algorithm_weights,
            eddCalculated=edd_calculated,
            storeIds=store_ids,
            errorCode=error_code,
            errorMessage=error_message,
            tags=tags,
            additionalData=additional_data,
        )

        log_info("Se envio trama TraceByOutput")
        return self.driver.send(trace.to_dict())

    def log_deprecated(
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
