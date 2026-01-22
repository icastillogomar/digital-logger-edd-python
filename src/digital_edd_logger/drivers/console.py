import json
from .base import BaseDriver


class ConsoleDriver(BaseDriver):

    def send(self, record: dict) -> str:
        print(json.dumps(record, indent=2, ensure_ascii=False, default=str))
        return "console-log"

    def close(self) -> None:
        pass
