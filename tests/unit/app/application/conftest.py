from typing import Any
from unittest.mock import AsyncMock

import pytest_asyncio

from app.application.notifications.notfication_gateway import (
    EmailNotificationGateway,
    SMSNotificationGateway,
)
from app.application.notifications.notification_service import NotificationService
from app.application.security.token_generator import TokenGenerator
from app.application.services.birthing_person_service import BirthingPersonService
from app.application.services.labour_service import LabourService
from app.application.services.subscriber_service import SubscriberService
from app.domain.birthing_person.entity import BirthingPerson
from app.domain.birthing_person.repository import BirthingPersonRepository
from app.domain.birthing_person.vo_birthing_person_id import BirthingPersonId
from app.domain.labour.entity import Labour
from app.domain.labour.repository import LabourRepository
from app.domain.labour.vo_labour_id import LabourId
from app.domain.subscriber.entity import Subscriber
from app.domain.subscriber.repository import SubscriberRepository
from app.domain.subscriber.vo_subscriber_id import SubscriberId


class MockBirthingPersonRepository(BirthingPersonRepository):
    _data = {}

    async def save(self, birthing_person: BirthingPerson) -> None:
        self._data[birthing_person.id_.value] = birthing_person

    async def delete(self, birthing_person: BirthingPerson) -> None:
        self._data.pop(birthing_person.id_.value)

    async def get_by_id(self, birthing_person_id: BirthingPersonId) -> BirthingPerson | None:
        return self._data.get(birthing_person_id.value, None)


class MockLabourRepository(LabourRepository):
    _data = {}

    async def save(self, labour_id: Labour) -> None:
        self._data[labour_id.id_.value] = labour_id

    async def delete(self, labour_id: Labour) -> None:
        self._data.pop(labour_id.id_.value)

    async def get_by_id(self, labour_id: LabourId) -> Labour | None:
        return self._data.get(labour_id.value, None)


class MockSubscriberRepository(SubscriberRepository):
    _data = {}

    async def save(self, birthing_person: Subscriber) -> None:
        self._data[birthing_person.id_.value] = birthing_person

    async def delete(self, birthing_person: Subscriber) -> None:
        self._data.pop(birthing_person.id_.value)

    async def get_by_id(self, birthing_person_id: SubscriberId) -> Subscriber | None:
        return self._data.get(birthing_person_id.value, None)


@pytest_asyncio.fixture
async def birthing_person_repo() -> BirthingPersonRepository:
    repo = MockBirthingPersonRepository()
    repo._data = {}
    return repo


@pytest_asyncio.fixture
async def subscriber_repo() -> SubscriberRepository:
    repo = MockSubscriberRepository()
    repo._data = {}
    return repo


@pytest_asyncio.fixture
async def labour_repo() -> LabourRepository:
    repo = MockLabourRepository()
    repo._data = {}
    return repo


class MockTokenGenerator(TokenGenerator):
    def generate(self, input: str) -> str:
        return input

    def validate(self, id: str, token: str):
        return token == id


class MockEmailNotificationGateway(EmailNotificationGateway):
    sent_notifications = []

    async def send(self, data: dict[str, Any]) -> None:
        self.sent_notifications.append(data)


class MockSMSNotificationGateway(SMSNotificationGateway):
    sent_notifications = []

    async def send(self, data: dict[str, Any]) -> None:
        self.sent_notifications.append(data)


@pytest_asyncio.fixture
async def birthing_person_service(
    birthing_person_repo: BirthingPersonRepository,
) -> BirthingPersonService:
    return BirthingPersonService(birthing_person_repo)


@pytest_asyncio.fixture
async def subscriber_service(
    subscriber_repo: SubscriberRepository,
) -> SubscriberService:
    return SubscriberService(
        subscriber_repository=subscriber_repo,
        token_generator=MockTokenGenerator(),
    )


@pytest_asyncio.fixture
async def labour_service(
    birthing_person_repo: BirthingPersonRepository,
    labour_repo: LabourRepository,
) -> LabourService:
    return LabourService(
        birthing_person_repository=birthing_person_repo,
        labour_repository=labour_repo,
        event_producer=AsyncMock(),
    )


@pytest_asyncio.fixture
async def notification_service() -> NotificationService:
    email_notification_gateway = MockEmailNotificationGateway()
    sms_notification_gateway = MockSMSNotificationGateway()
    email_notification_gateway.sent_notifications = []
    sms_notification_gateway.sent_notifications = []
    return NotificationService(
        email_notification_gateway=email_notification_gateway,
        sms_notification_gateway=sms_notification_gateway,
    )
