# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from datetime import timedelta
from typing import AsyncGenerator, Final

import pytest
from nats.js import JetStreamContext
from uuid_extensions import uuid7

from connect_four.domain import (
    ChipType,
    MoveRejectionReason,
    BOARD_COLUMNS,
    BOARD_ROWS,
    GameId,
    UserId,
    PlayerState,
    Move,
)
from connect_four.application import (
    LobbyId,
    GameCreatedEvent,
    GameStartedEvent,
    MoveAcceptedEvent,
    MoveRejectedEvent,
    GameEndReason,
    GameEndedEvent,
    Event,
)
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


@pytest.mark.parametrize(
    "event",
    [
        GameCreatedEvent(
            game_id=GameId(uuid7()),
            lobby_id=LobbyId(uuid7()),
            board=[[None] * BOARD_COLUMNS for _ in range(BOARD_ROWS)],
            players={
                _FIRST_PLAYER_ID: PlayerState(
                    chip_type=ChipType.FIRST,
                    time_left=timedelta(minutes=1),
                ),
                _SECOND_PLAYER_ID: PlayerState(
                    chip_type=ChipType.SECOND,
                    time_left=timedelta(minutes=1),
                ),
            },
            current_turn=_FIRST_PLAYER_ID,
        ),
        GameStartedEvent(game_id=GameId(uuid7())),
        MoveAcceptedEvent(
            game_id=GameId(uuid7()),
            move=Move(column=5, row=6),
            players={
                _FIRST_PLAYER_ID: PlayerState(
                    chip_type=ChipType.FIRST,
                    time_left=timedelta(seconds=50),
                ),
                _SECOND_PLAYER_ID: PlayerState(
                    chip_type=ChipType.SECOND,
                    time_left=timedelta(minutes=1),
                ),
            },
            current_turn=_SECOND_PLAYER_ID,
        ),
        MoveRejectedEvent(
            game_id=GameId(uuid7()),
            move=Move(column=0, row=0),
            reason=MoveRejectionReason.ILLEGAL_MOVE,
            players={
                _FIRST_PLAYER_ID: PlayerState(
                    chip_type=ChipType.FIRST,
                    time_left=timedelta(seconds=50),
                ),
                _SECOND_PLAYER_ID: PlayerState(
                    chip_type=ChipType.SECOND,
                    time_left=timedelta(minutes=1),
                ),
            },
            current_turn=_FIRST_PLAYER_ID,
        ),
        GameEndedEvent(
            game_id=GameId(uuid7()),
            move=Move(column=0, row=0),
            players={
                _FIRST_PLAYER_ID: PlayerState(
                    chip_type=ChipType.FIRST,
                    time_left=timedelta(seconds=50),
                ),
                _SECOND_PLAYER_ID: PlayerState(
                    chip_type=ChipType.SECOND,
                    time_left=timedelta(seconds=40),
                ),
            },
            reason=GameEndReason.DRAW,
            last_turn=_SECOND_PLAYER_ID,
        ),
    ],
)
async def test_nats_event_publisher(
    event: Event,
    nats_jetstream: JetStreamContext,
):
    event_publisher = NATSEventPublisher(
        jetstream=nats_jetstream,
        common_retort=common_retort_factory(),
    )
    await event_publisher.publish(event)
