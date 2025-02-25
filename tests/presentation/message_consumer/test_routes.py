# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from unittest.mock import AsyncMock
from datetime import datetime, timedelta, timezone

import pytest
from faststream import FastStream
from faststream.nats import NatsBroker, TestNatsBroker, TestApp
from dishka import Provider, Scope, AsyncContainer, make_async_container
from dishka.integrations.faststream import FastStreamProvider
from uuid_extensions import uuid7

from connect_four.application import (
    CreateGameProcessor,
    EndGameProcessor,
    MakeMoveProcessor,
)
from connect_four.infrastructure import get_env_var, common_retort_factory
from connect_four.presentation.message_consumer import (
    create_broker,
    create_game_command_factory,
    end_game_command_factory,
    make_move_command_factory,
    ContextVarSetter,
    operation_id_factory,
)
from connect_four.main.message_consumer import create_message_consumer_app


@pytest.fixture(scope="function")
def broker() -> NatsBroker:
    nats_url = get_env_var("TEST_NATS_URL")
    return create_broker(nats_url)


@pytest.fixture(scope="function")
def ioc_container() -> AsyncContainer:
    provider = Provider()

    provider.provide(operation_id_factory, scope=Scope.REQUEST)
    provider.provide(common_retort_factory, scope=Scope.APP)
    provider.provide(ContextVarSetter, scope=Scope.REQUEST)

    provider.provide(create_game_command_factory, scope=Scope.REQUEST)
    provider.provide(end_game_command_factory, scope=Scope.REQUEST)
    provider.provide(make_move_command_factory, scope=Scope.REQUEST)

    provider.provide(
        lambda: AsyncMock(),
        scope=Scope.REQUEST,
        provides=CreateGameProcessor,
    )
    provider.provide(
        lambda: AsyncMock(),
        scope=Scope.REQUEST,
        provides=EndGameProcessor,
    )
    provider.provide(
        lambda: AsyncMock(),
        scope=Scope.REQUEST,
        provides=MakeMoveProcessor,
    )

    return make_async_container(provider, FastStreamProvider())


@pytest.fixture(scope="function")
def app(broker: NatsBroker, ioc_container: AsyncContainer) -> FastStream:
    app = create_message_consumer_app(
        broker=broker,
        ioc_container=ioc_container,
    )
    return app


async def test_create_game(app: FastStream, broker: NatsBroker):
    async with (
        TestApp(app),
        TestNatsBroker(broker, with_real=True) as test_broker,
    ):
        message = {
            "game_id": uuid7().hex,
            "lobby_id": uuid7().hex,
            "first_player_id": uuid7().hex,
            "second_player_id": uuid7().hex,
            "time_for_each_player": timedelta(minutes=3),
            "created_at": datetime.now(timezone.utc),
        }
        await test_broker.publish(
            message=message,
            subject="game.created",
            stream="connection_hub",
        )


async def test_end_game(app: FastStream, broker: NatsBroker):
    async with (
        TestApp(app),
        TestNatsBroker(broker=broker, with_real=True) as test_broker,
    ):
        message = {"game_id": uuid7().hex}
        await test_broker.publish(
            message=message,
            subject="game.ended",
            stream="connection_hub",
        )


async def test_make_move(app: FastStream, broker: NatsBroker):
    async with (
        TestApp(app),
        TestNatsBroker(broker=broker, with_real=True) as test_broker,
    ):
        message = {
            "game_id": uuid7().hex,
            "move": {
                "column": 0,
                "row": 0,
            },
        }
        await test_broker.publish(
            message=message,
            subject="game.move_was_made",
            stream="api_gateway",
        )
