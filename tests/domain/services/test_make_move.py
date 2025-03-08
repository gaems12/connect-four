# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

import pytest
from datetime import datetime, timedelta, timezone
from typing import Final

from uuid_extensions import uuid7

from connect_four.domain import (
    GameId,
    GameStateId,
    UserId,
    ChipType,
    GameStatus,
    MoveRejectionReason,
    PlayerState,
    ChipLocation,
    Game,
    Draw,
    Win,
    MoveRejected,
    MakeMove,
)


_PLAYER_1_ID: Final = UserId(uuid7())
_PLAYER_2_ID: Final = UserId(uuid7())


def test_draw():
    players = {
        _PLAYER_1_ID: PlayerState(
            chip_type=ChipType.FIRST,
            time_left=timedelta(minutes=1),
        ),
        _PLAYER_2_ID: PlayerState(
            chip_type=ChipType.SECOND,
            time_left=timedelta(minutes=1),
        ),
    }

    #  x = ChipType.FIRST
    #  y = ChipType.SECOND
    #
    #  +---+---+---+---+---+---+
    #  | x | y | x | y | x |   |
    #  +---+---+---+---+---+---+
    #  | y | x | y | x | y | x |
    #  +---+---+---+---+---+---+
    #  | y | x | y | x | y | x |
    #  +---+---+---+---+---+---+
    #  | x | y | x | y | x | y |
    #  +---+---+---+---+---+---+
    #  | x | y | x | y | x | y |
    #  +---+---+---+---+---+---+
    #  | y | x | y | x | y | x |
    #  +---+---+---+---+---+---+
    #  | y | x | y | x | y | x |
    #  +---+---+---+---+---+---+

    board: list[list[ChipType | None]] = [
        [
            ChipType.FIRST,
            ChipType.SECOND,
            ChipType.FIRST,
            ChipType.SECOND,
            ChipType.FIRST,
            None,
        ],
        [
            ChipType.SECOND,
            ChipType.FIRST,
            ChipType.SECOND,
            ChipType.FIRST,
            ChipType.SECOND,
            ChipType.FIRST,
        ],
        [
            ChipType.SECOND,
            ChipType.FIRST,
            ChipType.SECOND,
            ChipType.FIRST,
            ChipType.SECOND,
            ChipType.FIRST,
        ],
        [
            ChipType.FIRST,
            ChipType.SECOND,
            ChipType.FIRST,
            ChipType.SECOND,
            ChipType.FIRST,
            ChipType.SECOND,
        ],
        [
            ChipType.FIRST,
            ChipType.SECOND,
            ChipType.FIRST,
            ChipType.SECOND,
            ChipType.FIRST,
            ChipType.SECOND,
        ],
        [
            ChipType.SECOND,
            ChipType.FIRST,
            ChipType.SECOND,
            ChipType.FIRST,
            ChipType.SECOND,
            ChipType.FIRST,
        ],
        [
            ChipType.SECOND,
            ChipType.FIRST,
            ChipType.SECOND,
            ChipType.FIRST,
            ChipType.SECOND,
            ChipType.FIRST,
        ],
    ]
    game = Game(
        id=GameId(uuid7()),
        state_id=GameStateId(uuid7()),
        status=GameStatus.IN_PROGRESS,
        players=players,
        current_turn=_PLAYER_1_ID,
        board=board,
        last_move_made_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )

    move_result = MakeMove()(
        game=game,
        current_player_id=_PLAYER_1_ID,
        column=5,
    )
    expected_move_result = Draw(ChipLocation(column=5, row=0))

    assert move_result == expected_move_result
    assert game.status == GameStatus.ENDED


@pytest.mark.parametrize(
    ["board", "column", "expected_chip_location"],
    [
        [
            #  x = ChipType.FIRST
            #  y = ChipType.SECOND
            #
            #  +---+---+---+---+---+---+
            #  |   |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  |   |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  |   |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  | y |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  | y |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  | y | y |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  | x | x | x |   |   |   |
            #  +---+---+---+---+---+---+
            [
                [None] * 6,
                [None] * 6,
                [None] * 6,
                [ChipType.SECOND] + [None] * 5,
                [ChipType.SECOND] + [None] * 5,
                [ChipType.SECOND, ChipType.FIRST] + [None] * 4,
                [ChipType.FIRST, ChipType.FIRST, ChipType.FIRST] + [None] * 3,
            ],
            3,
            ChipLocation(column=3, row=6),
        ],
        [
            #  x = ChipType.FIRST
            #  y = ChipType.SECOND
            #
            #  +---+---+---+---+---+---+
            #  |   |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  |   |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  |   |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  | x |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  | x |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  | x | y |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  | y | y | y |   |   |   |
            #  +---+---+---+---+---+---+
            [
                [None] * 6,
                [None] * 6,
                [None] * 6,
                [ChipType.FIRST] + [None] * 5,
                [ChipType.FIRST] + [None] * 5,
                [ChipType.FIRST] + [None] * 5,
                [ChipType.FIRST, ChipType.SECOND] + [None] * 4,
                [
                    ChipType.SECOND,
                    ChipType.SECOND,
                    ChipType.SECOND,
                ]
                + [None] * 3,
            ],
            0,
            ChipLocation(column=0, row=2),
        ],
        [
            #  x = ChipType.FIRST
            #  y = ChipType.SECOND
            #
            #  +---+---+---+---+---+---+
            #  |   |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  |   |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  |   |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  |   |   |   | x | y |   |
            #  +---+---+---+---+---+---+
            #  |   |   | x | y | y |   |
            #  +---+---+---+---+---+---+
            #  | y | x | x | y | x | y |
            #  +---+---+---+---+---+---+
            #  | x | y | y | x | y | x |
            #  +---+---+---+---+---+---+
            [
                [None] * 6,
                [None] * 6,
                [None] * 6,
                [None, None, None, ChipType.FIRST, ChipType.SECOND, None],
                [
                    None,
                    None,
                    ChipType.FIRST,
                    ChipType.SECOND,
                    ChipType.SECOND,
                    None,
                ],
                [
                    ChipType.SECOND,
                    ChipType.FIRST,
                    ChipType.FIRST,
                    ChipType.SECOND,
                    ChipType.FIRST,
                    ChipType.SECOND,
                ],
                [
                    ChipType.FIRST,
                    ChipType.SECOND,
                    ChipType.SECOND,
                    ChipType.FIRST,
                    ChipType.SECOND,
                    ChipType.FIRST,
                ],
            ],
            4,
            ChipLocation(column=4, row=2),
        ],
    ],
)
def test_win(
    board: list[list[ChipType | None]],
    column: int,
    expected_chip_location: ChipLocation,
):
    players = {
        _PLAYER_1_ID: PlayerState(
            chip_type=ChipType.FIRST,
            time_left=timedelta(minutes=1),
        ),
        _PLAYER_2_ID: PlayerState(
            chip_type=ChipType.SECOND,
            time_left=timedelta(minutes=1),
        ),
    }
    game = Game(
        id=GameId(uuid7()),
        state_id=GameStateId(uuid7()),
        status=GameStatus.IN_PROGRESS,
        players=players,
        current_turn=_PLAYER_1_ID,
        board=board,
        last_move_made_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )

    move_result = MakeMove()(
        game=game,
        current_player_id=_PLAYER_1_ID,
        column=column,
    )
    expected_move_result = Win(expected_chip_location)

    assert move_result == expected_move_result
    assert game.status == GameStatus.ENDED


@pytest.mark.parametrize(
    ["board", "column"],
    [
        [
            #  x = ChipType.FIRST
            #  y = ChipType.SECOND
            #
            #  +---+---+---+---+---+---+
            #  |   |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  |   |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  |   |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  |   |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  |   |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  |   |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  | x | y | y |   |   |   |
            #  +---+---+---+---+---+---+
            [
                [None] * 6,
                [None] * 6,
                [None] * 6,
                [None] * 6,
                [None] * 6,
                [None] * 6,
                [
                    ChipType.FIRST,
                    ChipType.SECOND,
                    ChipType.SECOND,
                ]
                + [None] * 3,
            ],
            6,
        ],
        [
            #  x = ChipType.FIRST
            #  y = ChipType.SECOND
            #
            #  +---+---+---+---+---+---+
            #  | x |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  | y |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  | x |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  | y |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  | x |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  | y |   |   |   |   |   |
            #  +---+---+---+---+---+---+
            #  | x | y | y |   |   |   |
            #  +---+---+---+---+---+---+
            [
                [ChipType.FIRST] + [None] * 5,
                [ChipType.SECOND] + [None] * 5,
                [ChipType.FIRST] + [None] * 5,
                [ChipType.SECOND] + [None] * 5,
                [ChipType.FIRST] + [None] * 5,
                [ChipType.SECOND] + [None] * 5,
                [
                    ChipType.FIRST,
                    ChipType.SECOND,
                    ChipType.SECOND,
                ]
                + [None] * 3,
            ],
            0,
        ],
    ],
)
def test_illegal_move(
    board: list[list[ChipType | None]],
    column: int,
):
    players = {
        _PLAYER_1_ID: PlayerState(
            chip_type=ChipType.FIRST,
            time_left=timedelta(minutes=1),
        ),
        _PLAYER_2_ID: PlayerState(
            chip_type=ChipType.SECOND,
            time_left=timedelta(minutes=1),
        ),
    }

    game = Game(
        id=GameId(uuid7()),
        state_id=GameStateId(uuid7()),
        status=GameStatus.IN_PROGRESS,
        players=players,
        current_turn=_PLAYER_1_ID,
        board=board,
        last_move_made_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )

    move_result = MakeMove()(
        game=game,
        current_player_id=_PLAYER_1_ID,
        column=column,
    )
    expected_move_result = MoveRejected(MoveRejectionReason.ILLEGAL_MOVE)

    assert move_result == expected_move_result
