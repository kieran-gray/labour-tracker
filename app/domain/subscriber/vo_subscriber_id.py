from dataclasses import dataclass

from app.domain.base.value_object import ValueObject


@dataclass(frozen=True, repr=False)
class SubscriberId(ValueObject):
    value: str
