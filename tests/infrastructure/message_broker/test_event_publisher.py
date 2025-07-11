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
    CommunicatonType,
    MoveRejectionReason,
    BOARD_COLUMNS,
    BOARD_ROWS,
    GameId,
    UserId,
    LobbyId,
    PlayerState,
    ChipLocation,
)
from connect_four.application import (
    GameCreatedEvent,
    MoveAcceptedEvent,
    MoveRejectedEvent,
    GameEndReason,
    GameEndedEvent,
    Event,
)
from connect_four.infrastructure import (
    OperationId,
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
                    communication_type=CommunicatonType.CENTRIFUGO,
                ),
                _SECOND_PLAYER_ID: PlayerState(
                    chip_type=ChipType.SECOND,
                    time_left=timedelta(minutes=1),
                    communication_type=CommunicatonType.CENTRIFUGO,
                ),
            },
            current_turn=_FIRST_PLAYER_ID,
        ),
        MoveAcceptedEvent(
            game_id=GameId(uuid7()),
            chip_location=ChipLocation(column=5, row=6),
            players={
                _FIRST_PLAYER_ID: PlayerState(
                    chip_type=ChipType.FIRST,
                    time_left=timedelta(seconds=50),
                    communication_type=CommunicatonType.CENTRIFUGO,
                ),
                _SECOND_PLAYER_ID: PlayerState(
                    chip_type=ChipType.SECOND,
                    time_left=timedelta(minutes=1),
                    communication_type=CommunicatonType.CENTRIFUGO,
                ),
            },
            current_turn=_SECOND_PLAYER_ID,
        ),
        MoveRejectedEvent(
            game_id=GameId(uuid7()),
            reason=MoveRejectionReason.ILLEGAL_MOVE,
            players={
                _FIRST_PLAYER_ID: PlayerState(
                    chip_type=ChipType.FIRST,
                    time_left=timedelta(seconds=50),
                    communication_type=CommunicatonType.CENTRIFUGO,
                ),
                _SECOND_PLAYER_ID: PlayerState(
                    chip_type=ChipType.SECOND,
                    time_left=timedelta(minutes=1),
                    communication_type=CommunicatonType.CENTRIFUGO,
                ),
            },
            current_turn=_FIRST_PLAYER_ID,
        ),
        GameEndedEvent(
            game_id=GameId(uuid7()),
            chip_location=ChipLocation(column=0, row=0),
            players={
                _FIRST_PLAYER_ID: PlayerState(
                    chip_type=ChipType.FIRST,
                    time_left=timedelta(seconds=50),
                    communication_type=CommunicatonType.CENTRIFUGO,
                ),
                _SECOND_PLAYER_ID: PlayerState(
                    chip_type=ChipType.SECOND,
                    time_left=timedelta(seconds=40),
                    communication_type=CommunicatonType.CENTRIFUGO,
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
        operation_id=OperationId(uuid7()),
    )
    await event_publisher.publish(event)
