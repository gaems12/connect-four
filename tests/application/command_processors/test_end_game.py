# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

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
    Game,
    PlayerState,
    EndGame,
)
from connect_four.application import (
    TryToLoseOnTimeTask,
    EndGameCommand,
    EndGameProcessor,
)
from .fakes import FakeGameGateway, FakeTaskScheduler


_GAME_ID: Final = GameId(uuid7())
_GAME_STATE_ID: Final = GameStateId(uuid7())

_FIRST_PLAYER_ID: Final = UserId(uuid7())
_SECOND_PLAYER_ID: Final = UserId(uuid7())

_TIME_LEFT_FOR_FIRST_PLAYER: Final = timedelta(seconds=20)
_TIME_LEFT_FOR_SECOND_SECOND: Final = timedelta(minutes=1)


async def test_end_game_processor():
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

    task = TryToLoseOnTimeTask(
        id=_GAME_STATE_ID,
        execute_at=_TIME_LEFT_FOR_FIRST_PLAYER,
        game_id=_GAME_ID,
        game_state_id=_GAME_STATE_ID,
    )
    task_scheduler = FakeTaskScheduler({_GAME_STATE_ID: task})

    command = EndGameCommand(game_id=_GAME_ID)
    command_processor = EndGameProcessor(
        end_game=EndGame(),
        game_gateway=game_gateway,
        task_scheduler=task_scheduler,
        transaction_manager=AsyncMock(),
    )

    await command_processor.process(command)

    assert game_gateway.games
    assert game_gateway.games[0].status == GameStatus.ENDED

    assert not task_scheduler.tasks
