from dataclasses import dataclass
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4

from app.domain.base.entity import Entity
from app.domain.constants.contraction import CONTRACTION_MAX_INTENSITY, CONTRACTION_MIN_INTENSITY
from app.domain.exceptions.contraction import ContractionIntensityInvalid
from app.domain.value_objects.contraction_duration import Duration
from app.domain.value_objects.contraction_id import ContractionId


@dataclass(eq=False, kw_only=True)
class Contraction(Entity[ContractionId]):
    """
    Domain entity representing a single contraction during labor.
    Unlike Duration which is just a value object, Contraction has identity
    and carries additional domain-relevant information.
    """

    duration: Duration
    intensity: int
    labor_session_id: UUID
    notes: str | None = None
    created_at: datetime = None

    def __post_init__(self):
        """Validate the contraction upon initialization"""
        if self.intensity < CONTRACTION_MIN_INTENSITY or self.intensity > CONTRACTION_MAX_INTENSITY:
            raise ContractionIntensityInvalid()

        if self.created_at is None:
            self.created_at = datetime.now()

    @classmethod
    def start(
        cls,
        labor_session_id: UUID,
        intensity: int,
        start_time: datetime | None = None,
        contraction_id: UUID | None = None,
        notes: str | None = None,
    ) -> Self:
        """
        Start a new contraction. Note this is a partially initialized contraction
        since it doesn't have an end time yet.
        """
        # Using a temporary end time equal to start time - will be updated when contraction ends
        start_time = start_time or datetime.now()
        contraction_id = contraction_id or uuid4()
        return cls(
            id_=ContractionId(contraction_id),
            duration=Duration(start_time=start_time, end_time=start_time),
            intensity=intensity,
            labor_session_id=labor_session_id,
            notes=notes,
        )

    def end(self, end_time: datetime) -> None:
        """End the contraction by setting its final duration"""
        new_duration = Duration(start_time=self.duration.start_time, end_time=end_time)
        self.duration = new_duration

    @property
    def is_active(self) -> bool:
        """Check if this is an active contraction"""
        return self.duration.start_time == self.duration.end_time

    @property
    def start_time(self) -> datetime:
        """Get the start time of the contraction"""
        return self.duration.start_time

    @property
    def end_time(self) -> datetime:
        """Get the end time of the contraction"""
        return self.duration.end_time

    def update_intensity(self, intensity: int) -> None:
        """Update the intensity of the contraction"""
        if intensity < CONTRACTION_MIN_INTENSITY or intensity > CONTRACTION_MAX_INTENSITY:
            raise ContractionIntensityInvalid()
        self.intensity = intensity

    def add_notes(self, notes: str) -> None:
        """Add or update notes for this contraction"""
        self.notes = notes
