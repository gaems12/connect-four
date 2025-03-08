# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from unittest.mock import AsyncMock
from datetime import datetime, timedelta, timezone
from typing import Final

from uuid_extensions import uuid7

from connect_four.domain import (
    GameStatus,
    ChipType,
    GameId,
    GameStateId,
    UserId,
    PlayerState,
    Game,
    TryToLoseByTime,
)
from connect_four.application import (
    GameEndReason,
    GameEndedEvent,
    TryToLoseByTimeCommand,
    TryToLoseByTimeProcessor,
)
from .fakes import (
    FakeGameGateway,
    FakeEventPublisher,
    FakeCentrifugoClient,
)


_GAME_ID: Final = GameId(uuid7())
_GAME_STATE_ID: Final = GameStateId(uuid7())

_FIRST_PLAYER_ID: Final = UserId(uuid7())
_SECOND_PLAYER_ID: Final = UserId(uuid7())

_TIME_LEFT_FOR_FIRST_PLAYER: Final = timedelta(seconds=20)
_TIME_LEFT_FOR_SECOND_PLAYER: Final = timedelta(minutes=1)


async def test_lose_by_time_processor():
    players = {
        _FIRST_PLAYER_ID: PlayerState(
            chip_type=ChipType.FIRST,
            time_left=_TIME_LEFT_FOR_FIRST_PLAYER,
        ),
        _SECOND_PLAYER_ID: PlayerState(
            chip_type=ChipType.SECOND,
            time_left=_TIME_LEFT_FOR_SECOND_PLAYER,
        ),
    }
    board: list[list[ChipType | None]] = [
        [None] * 6,
        [None] * 6,
        [None] * 6,
        [ChipType.SECOND] + [None] * 5,
        [ChipType.SECOND] + [None] * 5,
        [ChipType.SECOND, ChipType.FIRST] + [None] * 4,
        [ChipType.FIRST, ChipType.FIRST, ChipType.FIRST] + [None] * 3,
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
        created_at=(
            datetime.now(timezone.utc) - timedelta(minutes=1, seconds=20)
        ),
    )

    game_gateway = FakeGameGateway({_GAME_ID: game})
    event_publisher = FakeEventPublisher([])
    centrifugo_client = FakeCentrifugoClient({})

    command = TryToLoseByTimeCommand(
        game_id=_GAME_ID,
        game_state_id=_GAME_STATE_ID,
    )
    command_processor = TryToLoseByTimeProcessor(
        try_to_lose_by_time=TryToLoseByTime(),
        game_gateway=game_gateway,
        event_publisher=event_publisher,
        centrifugo_client=centrifugo_client,
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
            time_left=_TIME_LEFT_FOR_SECOND_PLAYER,
        ),
    }
    expected_event = GameEndedEvent(
        game_id=_GAME_ID,
        chip_location=None,
        players=updated_players,
        reason=GameEndReason.LOSS_BY_TIME,
        last_turn=_FIRST_PLAYER_ID,
    )
    assert expected_event in event_publisher.events

    centrifugo_publication_players = {
        _FIRST_PLAYER_ID.hex: {
            "chip_type": ChipType.FIRST,
            "time_left": timedelta(seconds=0).total_seconds(),
        },
        _SECOND_PLAYER_ID.hex: {
            "chip_type": ChipType.SECOND,
            "time_left": _TIME_LEFT_FOR_SECOND_PLAYER.total_seconds(),
        },
    }
    expected_centrifugo_publication = {
        "type": "game_ended",
        "chip_location": None,
        "players": centrifugo_publication_players,
        "reason": GameEndReason.LOSS_BY_TIME,
        "last_turn": game.current_turn.hex,
    }
    assert (
        centrifugo_client.publications[f"games:{_GAME_ID.hex}"]
        == expected_centrifugo_publication
    )
