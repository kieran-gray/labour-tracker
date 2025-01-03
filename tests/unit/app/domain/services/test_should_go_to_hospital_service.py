from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.domain.birthing_person.vo_birthing_person_id import BirthingPersonId
from app.domain.labour.constants import (
    CONTRACTIONS_REQUIRED_NULLIPAROUS,
    CONTRACTIONS_REQUIRED_PAROUS,
    LENGTH_OF_CONTRACTIONS_MINUTES,
    TIME_BETWEEN_CONTRACTIONS_NULLIPAROUS,
    TIME_BETWEEN_CONTRACTIONS_PAROUS,
)
from app.domain.labour.entity import Labour
from app.domain.services.should_go_to_hospital import ShouldGoToHospitalService
from tests.unit.app.conftest import get_contractions


@pytest.fixture
def labour() -> Labour:
    return Labour.begin(
        labour_id=UUID("12345678-1234-5678-1234-567812345678"),
        birthing_person_id=BirthingPersonId("87654321-4321-1234-8765-567812345678"),
        start_time=datetime.now(UTC),
        first_labour=True,
    )


def test_should_go_to_hospital_returns_false(labour: Labour):
    assert not ShouldGoToHospitalService().should_go_to_hospital(labour)


def test_should_go_to_hospital_returns_true_parous(labour: Labour):
    contractions = get_contractions(
        labour_id=labour.id_.value,
        number_of_contractions=CONTRACTIONS_REQUIRED_PAROUS,
        length_of_contractions=LENGTH_OF_CONTRACTIONS_MINUTES,
        time_between_contractions=TIME_BETWEEN_CONTRACTIONS_PAROUS,
    )
    labour.first_labour = False
    labour.contractions = contractions
    assert ShouldGoToHospitalService().should_go_to_hospital(labour)


def test_should_go_to_hospital_returns_true_nulliparous(labour: Labour):
    contractions = get_contractions(
        labour_id=labour.id_.value,
        number_of_contractions=CONTRACTIONS_REQUIRED_NULLIPAROUS,
        length_of_contractions=LENGTH_OF_CONTRACTIONS_MINUTES,
        time_between_contractions=TIME_BETWEEN_CONTRACTIONS_NULLIPAROUS,
    )
    labour.contractions = contractions
    assert ShouldGoToHospitalService().should_go_to_hospital(labour)


def test_should_go_to_hospital_returns_false_when_contractions_too_far_apart(labour: Labour):
    contractions = get_contractions(
        labour_id=labour.id_.value,
        number_of_contractions=CONTRACTIONS_REQUIRED_NULLIPAROUS,
        length_of_contractions=LENGTH_OF_CONTRACTIONS_MINUTES,
        time_between_contractions=TIME_BETWEEN_CONTRACTIONS_NULLIPAROUS + 1,
    )

    labour.contractions = contractions
    assert not ShouldGoToHospitalService().should_go_to_hospital(labour)
