# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from unittest.mock import AsyncMock
from datetime import datetime, timedelta, timezone
from typing import Final

from uuid_extensions import uuid7

from four_in_a_row.domain import (
    GameStatus,
    ChipType,
    GameId,
    GameStateId,
    UserId,
    PlayerState,
    Game,
    TryToLoseOnTime,
)
from four_in_a_row.application import (
    GameEndReason,
    GameEndedEvent,
    LoseOnTimeCommand,
    LoseOnTimeProcessor,
)
from .fakes import FakeGameGateway, FakeEventPublisher


_GAME_ID: Final = GameId(uuid7())
_GAME_STATE_ID: Final = GameStateId(uuid7())

_FIRST_PLAYER_ID: Final = UserId(uuid7())
_SECOND_PLAYER_ID: Final = UserId(uuid7())

_TIME_LEFT_FOR_FIRST_PLAYER: Final = timedelta(seconds=20)
_TIME_LEFT_FOR_SECOND_SECOND: Final = timedelta(minutes=1)


async def test_lose_on_time_processor():
    players = {
        _FIRST_PLAYER_ID: PlayerState(
            chip_type=ChipType.FIRST,
            time_left=_TIME_LEFT_FOR_FIRST_PLAYER,
        ),
        _SECOND_PLAYER_ID: PlayerState(
            chip_type=ChipType.SECOND,
            time_left=_TIME_LEFT_FOR_SECOND_SECOND,
        ),
    }
    board = [
        [
            [None] * 6,
            [None] * 6,
            [None] * 6,
            [ChipType.SECOND] + [None] * 5,
            [ChipType.SECOND] + [None] * 5,
            [ChipType.SECOND, ChipType.FIRST] + [None] * 4,
            [ChipType.FIRST, ChipType.FIRST, ChipType.FIRST] + [None] * 3,
        ],
    ]

    game = Game(
        id=_GAME_ID,
        state_id=_GAME_STATE_ID,
        status=GameStatus.IN_PROGRESS,
        players=players,
        current_turn=_FIRST_PLAYER_ID,
        board=board,
        last_move_made_at=(
            datetime.now(timezone.utc) - _TIME_LEFT_FOR_FIRST_PLAYER
        ),
        created_at=datetime.now(timezone.utc),
    )

    game_gateway = FakeGameGateway({_GAME_ID: game})
    event_publisher = FakeEventPublisher([])

    command = LoseOnTimeCommand(
        game_id=_GAME_ID,
        game_state_id=_GAME_STATE_ID,
    )
    command_processor = LoseOnTimeProcessor(
        try_to_lose_on_time=TryToLoseOnTime(),
        game_gateway=game_gateway,
        event_publisher=event_publisher,
        transaction_manager=AsyncMock(),
    )

    await command_processor.process(command)

    updated_players = {
        _FIRST_PLAYER_ID: PlayerState(
            chip_type=ChipType.FIRST,
            time_left=timedelta(seconds=0),
        ),
        _SECOND_PLAYER_ID: PlayerState(
            chip_type=ChipType.SECOND,
            time_left=_TIME_LEFT_FOR_SECOND_SECOND,
        ),
    }
    expected_event = GameEndedEvent(
        game_id=_GAME_ID,
        move=None,
        players=updated_players,
        reason=GameEndReason.TIME_IS_UP,
        last_turn=_FIRST_PLAYER_ID,
    )
    assert expected_event in event_publisher.events
