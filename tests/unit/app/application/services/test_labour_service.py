from copy import deepcopy
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide

from app.application.events.producer import EventProducer
from app.application.services.labour_service import LabourService
from app.domain.birthing_person.entity import BirthingPerson
from app.domain.birthing_person.exceptions import BirthingPersonNotFoundById
from app.domain.birthing_person.repository import BirthingPersonRepository
from app.domain.birthing_person.vo_birthing_person_id import BirthingPersonId
from app.domain.labour.entity import Labour
from app.domain.labour.repository import LabourRepository
from app.domain.labour.vo_labour_id import LabourId

BIRTHING_PERSON = "bp_id"


class MockLabourRepository(LabourRepository):
    _data = {}
    _initial_data = {}

    def reset(self):
        self._data = deepcopy(self._initial_data)

    async def save(self, labour_id: Labour) -> None:
        self._data[labour_id.id_.value] = labour_id

    async def delete(self, labour_id: Labour) -> None:
        self._data.pop(labour_id.id_.value)

    async def get_by_id(self, labour_id: LabourId) -> Labour | None:
        return self._data.get(labour_id.value, None)


class MockBirthingPersonRepository(BirthingPersonRepository):
    _data = {}
    _initial_data = {
        BIRTHING_PERSON: BirthingPerson(
            id_=BirthingPersonId(BIRTHING_PERSON),
            first_name="Name",
            last_name="User",
            first_labour=True,
            labours=[],
        )
    }

    def reset(self) -> None:
        self._data = deepcopy(self._initial_data)

    async def save(self, birthing_person: BirthingPerson) -> None:
        self._data[birthing_person.id_.value] = birthing_person

    async def delete(self, birthing_person: BirthingPerson) -> None:
        self._data.pop(birthing_person.id_.value)

    async def get_by_id(self, birthing_person_id: BirthingPersonId) -> BirthingPerson | None:
        return self._data.get(birthing_person_id.value, None)


class MockLabourRepositoryProvider(Provider):
    scope = Scope.APP

    @provide
    def get_birthing_person_repository(self) -> LabourRepository:
        return MockLabourRepository()


class MockBirthingPersonRepositoryProvider(Provider):
    scope = Scope.APP

    @provide
    def get_birthing_person_repository(self) -> BirthingPersonRepository:
        return MockBirthingPersonRepository()


@pytest_asyncio.fixture
async def container():
    container = make_async_container(
        MockLabourRepositoryProvider(),
        MockBirthingPersonRepositoryProvider(),
    )
    yield container
    await container.close()


@pytest_asyncio.fixture
async def labour_repo(container: AsyncContainer):
    repo = await container.get(LabourRepository)
    repo.reset()
    return repo


@pytest_asyncio.fixture
async def birthing_person_repo(container: AsyncContainer):
    repo = await container.get(BirthingPersonRepository)
    repo.reset()
    return repo


@pytest_asyncio.fixture
def event_producer():
    return AsyncMock()


@pytest_asyncio.fixture
async def labour_service(
    labour_repo: LabourRepository,
    birthing_person_repo: BirthingPersonRepository,
    event_producer: EventProducer,
) -> LabourService:
    return LabourService(
        birthing_person_repository=birthing_person_repo,
        labour_repository=labour_repo,
        event_producer=event_producer,
    )


async def test_can_begin_labour(labour_service: LabourService) -> None:
    await labour_service.begin_labour(BIRTHING_PERSON)


async def test_cannot_begin_labour_for_non_existent_user(labour_service: LabourService) -> None:
    with pytest.raises(BirthingPersonNotFoundById):
        await labour_service.begin_labour("TEST123456")


async def test_can_complete_labour(labour_service: LabourService) -> None:
    await labour_service.begin_labour(BIRTHING_PERSON)
    await labour_service.complete_labour(BIRTHING_PERSON)


async def test_cannot_complete_labour_for_non_existent_user(labour_service: LabourService) -> None:
    with pytest.raises(BirthingPersonNotFoundById):
        await labour_service.complete_labour("TEST123456")


async def test_can_start_contraction(labour_service: LabourService) -> None:
    await labour_service.begin_labour(BIRTHING_PERSON)
    await labour_service.start_contraction(BIRTHING_PERSON)


async def test_cannot_start_contraction_for_non_existent_user(
    labour_service: LabourService,
) -> None:
    with pytest.raises(BirthingPersonNotFoundById):
        await labour_service.start_contraction("TEST123456")


async def test_can_end_contraction(labour_service: LabourService) -> None:
    await labour_service.begin_labour(BIRTHING_PERSON)
    await labour_service.start_contraction(BIRTHING_PERSON)
    await labour_service.end_contraction(BIRTHING_PERSON, intensity=5)


async def test_cannot_end_contraction_for_non_existent_user(labour_service: LabourService) -> None:
    with pytest.raises(BirthingPersonNotFoundById):
        await labour_service.end_contraction("TEST123456", intensity=5)
