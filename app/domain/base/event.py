import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Self


@dataclass
class DomainEvent:
    """Base class for all domain events"""

    id: str
    type: str
    data: dict[str, Any]
    time: datetime

    @classmethod
    def create(cls, event_type: str, data: dict[str, Any]) -> Self:
        return cls(id=str(uuid.uuid4()), type=event_type, data=data, time=datetime.now())

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "type": self.type, "data": self.data, "time": self.time.isoformat()}