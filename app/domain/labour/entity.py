from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Self
from uuid import UUID, uuid4

from app.domain.base.entity import Entity
from app.domain.birthing_person.vo_birthing_person_id import BirthingPersonId
from app.domain.contraction.entity import Contraction
from app.domain.labour.enums import LabourPhase
from app.domain.labour.vo_labour_id import LabourId


@dataclass(eq=False, kw_only=True)
class Labour(Entity[LabourId]):
    """
    Aggregate root for tracking labour.
    Maintains consistency across all contractions and enforces labour-specific rules.
    """

    birthing_person_id: BirthingPersonId
    start_time: datetime
    first_labour: bool
    contractions: list[Contraction] = field(default_factory=list)
    current_phase: LabourPhase = LabourPhase.EARLY
    end_time: datetime | None = None
    notes: str | None = None

    @classmethod
    def begin(
        cls,
        birthing_person_id: BirthingPersonId,
        first_labour: bool,
        labour_id: UUID | None = None,
        start_time: datetime | None = None,
    ) -> Self:
        """Begin a new labour."""
        return cls(
            id_=LabourId(labour_id or uuid4()),
            birthing_person_id=birthing_person_id,
            start_time=start_time or datetime.now(),
            first_labour=first_labour,
            contractions=[],
        )

    @property
    def is_active(self) -> bool:
        return self.end_time is None

    @property
    def active_contraction(self) -> Contraction | None:
        """Get the currently active contraction, if any"""
        return next(
            (contraction for contraction in self.contractions if contraction.is_active),
            None,
        )

    @property
    def has_active_contraction(self) -> bool:
        """Check if there's currently an active contraction"""
        return any(contraction.is_active for contraction in self.contractions)

    def start_contraction(
        self,
        intensity: int | None = None,
        start_time: datetime | None = None,
        notes: str | None = None,
    ) -> Contraction:
        """Start a new contraction in this session"""
        contraction = Contraction.start(
            labour_id=self.id_,
            start_time=start_time,
            intensity=intensity,
            notes=notes,
        )
        self.contractions.append(contraction)
        return contraction

    def end_contraction(
        self,
        intensity: int | None = None,
        end_time: datetime | None = None,
        notes: str | None = None,
    ) -> None:
        """End the currently active contraction"""
        assert self.active_contraction
        if intensity:
            self.active_contraction.intensity = intensity
        if notes:
            self.active_contraction.notes = notes
        self.active_contraction.end(end_time or datetime.now())
        self._update_labour_phase()

    def _update_labour_phase(self) -> None:
        """
        Update the labour phase based on contraction patterns.
        This is a simplified version - in reality, this would likely involve
        additional medical data like dilation measurements.
        """
        recent_contractions = self.contractions[-5:]  # Look at last 5 contractions
        avg_intensity = sum(c.intensity for c in recent_contractions if c.intensity) / len(
            recent_contractions
        )
        avg_duration = sum(c.duration.duration_minutes for c in recent_contractions) / len(
            recent_contractions
        )

        # Simplified phase determination logic
        if avg_intensity >= 8 and avg_duration >= 1.5:
            self.current_phase = LabourPhase.TRANSITION
        elif avg_intensity >= 6 and avg_duration >= 1:
            self.current_phase = LabourPhase.ACTIVE

    def complete_labour(self, end_time: datetime | None = None, notes: str | None = None) -> None:
        """Mark the labour as complete"""
        self.end_time = end_time or datetime.now()
        self.current_phase = LabourPhase.COMPLETE
        if notes:
            self.notes = notes

    def get_contraction_pattern(self) -> dict[str, Any] | None:
        """Analyze the current contraction pattern"""
        if len(self.contractions) < 3:
            return None

        recent = self.contractions[-3:]

        avg_duration = sum(c.duration.duration_minutes for c in recent) / len(recent)
        avg_intensity = sum(c.intensity for c in recent if c.intensity) / len(recent)

        # Calculate average time between contractions
        intervals = []
        for prev, curr in zip(recent, recent[1:], strict=False):
            interval = (curr.start_time - prev.end_time).total_seconds() / 60
            intervals.append(interval)
        avg_interval = sum(intervals) / len(intervals)

        return {
            "average_duration_minutes": round(avg_duration, 1),
            "average_intensity": round(avg_intensity, 1),
            "average_interval_minutes": round(avg_interval, 1),
            "phase": self.current_phase.value,
        }
