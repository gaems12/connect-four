# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from datetime import timedelta
from typing import AsyncGenerator, Final

import pytest
from nats.js import JetStreamContext
from uuid_extensions import uuid7

from connect_four.domain import ChipType, GameId, UserId, PlayerState, Move
from connect_four.application import GameEndReason, GameEndedEvent
from connect_four.infrastructure import (
    common_retort_factory,
    NATSConfig,
    nats_client_factory,
    nats_jetstream_factory,
    NATSEventPublisher,
)


_FIRST_PLAYER_ID: Final = UserId(uuid7())
_SECOND_PLAYER_ID: Final = UserId(uuid7())


@pytest.fixture(scope="function")
async def nats_jetstream(
    nats_config: NATSConfig,
) -> AsyncGenerator[JetStreamContext, None]:
    async for nats_client in nats_client_factory(nats_config):
        yield nats_jetstream_factory(nats_client)


async def test_nats_event_publisher(nats_jetstream: JetStreamContext):
    event_publisher = NATSEventPublisher(
        jetstream=nats_jetstream,
        common_retort=common_retort_factory(),
    )

    players = {
        _FIRST_PLAYER_ID: PlayerState(
            chip_type=ChipType.FIRST,
            time_left=timedelta(seconds=50),
        ),
        _SECOND_PLAYER_ID: PlayerState(
            chip_type=ChipType.SECOND,
            time_left=timedelta(seconds=40),
        ),
    }
    event = GameEndedEvent(
        game_id=GameId(uuid7()),
        move=Move(column=0, row=0),
        players=players,
        reason=GameEndReason.DRAW,
        last_turn=_SECOND_PLAYER_ID,
    )

    await event_publisher.publish(event)
