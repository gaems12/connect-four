# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from unittest.mock import AsyncMock

import pytest
from taskiq import TaskiqMessage, InMemoryBroker
from taskiq.formatters.proxy_formatter import ProxyFormatter
from dishka import Provider, Scope, AsyncContainer, make_async_container
from dishka.integrations.faststream import FastStreamProvider
from uuid_extensions import uuid7

from connect_four.domain import GameId, GameStateId
from connect_four.application import (
    TryToLoseOnTimeCommand,
    TryToLoseOnTimeProcessor,
)
from connect_four.infrastructure import OperationId
from connect_four.presentation.task_executor import create_broker
from connect_four.main.task_executor import create_task_executor_app


@pytest.fixture(scope="function")
def ioc_container() -> AsyncContainer:
    provider = Provider()

    provider.provide(
        lambda: AsyncMock(),
        scope=Scope.REQUEST,
        provides=TryToLoseOnTimeProcessor,
    )

    return make_async_container(provider, FastStreamProvider())


@pytest.fixture(scope="function")
async def app(ioc_container: AsyncContainer) -> InMemoryBroker:
    broker = create_broker()

    app = create_task_executor_app(
        broker=broker,
        ioc_container=ioc_container,
    )
    await app.startup()

    return app


async def test_try_to_lose_on_time(app: InMemoryBroker) -> None:
    taskiq_message = TaskiqMessage(
        task_id=uuid7().hex,
        task_name="try_to_lose_on_time",
        labels={},
        labels_types=None,
        args=[OperationId(uuid7())],
        kwargs={
            "command": TryToLoseOnTimeCommand(
                game_id=GameId(uuid7()),
                game_state_id=GameStateId(uuid7()),
            ),
        },
    )

    proxy_formatter = ProxyFormatter(app)
    broker_message = proxy_formatter.dumps(taskiq_message)

    await app.kick(broker_message)
