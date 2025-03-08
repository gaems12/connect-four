# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from unittest.mock import AsyncMock

import pytest
from taskiq import TaskiqMessage, InMemoryBroker
from taskiq.formatters.proxy_formatter import ProxyFormatter
from dishka import Provider, Scope, AsyncContainer, make_async_container
from dishka.integrations.taskiq import TaskiqProvider, setup_dishka
from uuid_extensions import uuid7

from connect_four.domain import GameId, GameStateId
from connect_four.application import (
    TryToLoseByTimeCommand,
    TryToLoseByTimeProcessor,
)
from connect_four.infrastructure import OperationId
from connect_four.presentation.task_executor import create_broker


@pytest.fixture(scope="function")
def ioc_container() -> AsyncContainer:
    provider = Provider()

    provider.provide(
        lambda: AsyncMock(),
        scope=Scope.REQUEST,
        provides=TryToLoseByTimeProcessor,
    )

    return make_async_container(provider, TaskiqProvider())


@pytest.fixture(scope="function")
async def app(ioc_container: AsyncContainer) -> InMemoryBroker:
    broker = create_broker()
    setup_dishka(ioc_container, broker)

    await broker.startup()

    return broker


async def test_try_to_lose_on_time(app: InMemoryBroker) -> None:
    taskiq_message = TaskiqMessage(
        task_id=uuid7().hex,
        task_name="try_to_lose_by_time",
        labels={},
        labels_types=None,
        args=[OperationId(uuid7())],
        kwargs={
            "command": TryToLoseByTimeCommand(
                game_id=GameId(uuid7()),
                game_state_id=GameStateId(uuid7()),
            ),
        },
    )

    proxy_formatter = ProxyFormatter(app)
    broker_message = proxy_formatter.dumps(taskiq_message)

    await app.kick(broker_message)
