import json
from typing import Any

from app.application.interfaces.notfication_gateway import NotificationGateway


class LocalStorageNotificationGateway(NotificationGateway):
    """Notification gateway that saves events to local storage"""

    def send(self, data: dict[str, Any]) -> None:
        with open(f"{data.get("type")}_{data.get("time")}", "w") as f:
            json.dump(data, f)