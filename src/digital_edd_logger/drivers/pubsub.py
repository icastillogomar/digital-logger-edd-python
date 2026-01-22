import os
import json
from .base import BaseDriver
from ..utils import log_info


class PubSubDriver(BaseDriver):

    def __init__(self, project_id: str = None, topic_name: str = None):
        self.topic_name = topic_name or os.getenv("PUBSUB_TOPIC_NAME", "digital-edd-sdk")
        self.publish_enabled = os.getenv("SDKTRACKING_PUBLISH", "true") == "true"
        self._client = None
        self._topic = None
        self._project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")

        if not self._project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT no está configurado.")

    def _ensure_client(self):
        if self._client is not None:
            return
        
        from google.cloud import pubsub_v1
        
        self._client = pubsub_v1.PublisherClient()
        self._topic = self._client.topic_path(self._project_id, self.topic_name)
        log_info(f"PubSub conectado al topic: {self.topic_name}")

    def send(self, record: dict) -> str:
        if not self.publish_enabled:
            return "publish-disabled"
        
        self._ensure_client()
        data = json.dumps(record, ensure_ascii=False, default=str).encode("utf-8")
        future = self._client.publish(self._topic, data)
        return future.result()

    def close(self) -> None:
        pass
