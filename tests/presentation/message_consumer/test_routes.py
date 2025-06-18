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
from connect_four.infrastructure import NATSConfig
from connect_four.presentation.message_consumer import (
    create_game,
    end_game,
    make_move,
    create_broker,
)
from connect_four.main.message_consumer import create_message_consumer_app


@pytest.fixture(scope="function")
def broker(nats_config: NATSConfig) -> NatsBroker:
    return create_broker(nats_config.url)


@pytest.fixture(scope="function")
def ioc_container() -> AsyncContainer:
    provider = Provider()

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
            subject="gaems12.connection_hub.connect_four.game.created",
            stream="games",
        )
        await create_game.wait_call(1)


async def test_end_game(app: FastStream, broker: NatsBroker):
    async with (
        TestApp(app),
        TestNatsBroker(broker=broker, with_real=True) as test_broker,
    ):
        message = {"game_id": uuid7().hex}
        await test_broker.publish(
            message=message,
            subject="gaems12.connection_hub.connect_four.game.player_disqualified",
            stream="games",
        )
        await end_game.wait_call(1)


async def test_make_move(app: FastStream, broker: NatsBroker):
    async with (
        TestApp(app),
        TestNatsBroker(broker=broker, with_real=True) as test_broker,
    ):
        message = {
            "current_user_id": uuid7().hex,
            "game_id": uuid7().hex,
            "column": 0,
        }
        await test_broker.publish(
            message=message,
            subject="gaems12.api_gateway.connect_four.game.move_was_made",
            stream="games",
        )
        await make_move.wait_call(1)
