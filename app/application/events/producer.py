from typing import Protocol

from app.domain.base.event import DomainEvent


class EventProducer(Protocol):
    """Protocol for event producers"""

    async def publish(self, event: DomainEvent) -> None:
        """Publish single event."""

    async def publish_batch(self, events: list[DomainEvent]) -> None:
        """Publish batch of events."""
