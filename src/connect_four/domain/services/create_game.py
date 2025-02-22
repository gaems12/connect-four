# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from datetime import datetime, timedelta
from uuid import uuid4

from connect_four.domain.identitifiers import GameId, GameStateId, UserId
from connect_four.domain.constants import (
    ChipType,
    GameStatus,
    BOARD_COLUMNS,
    BOARD_ROWS,
)
from connect_four.domain.models import Game, PlayerState


class CreateGame:
    def __call__(
        self,
        *,
        id: GameId,
        first_player_id: UserId,
        second_player_id: UserId,
        created_at: datetime,
        time_for_each_player: timedelta,
        last_game: Game | None = None,
    ) -> Game:
        if last_game:
            players = {
                first_player_id: PlayerState(
                    chip_type=last_game.players[second_player_id].chip_type,
                    time_left=time_for_each_player,
                ),
                second_player_id: PlayerState(
                    chip_type=last_game.players[first_player_id].chip_type,
                    time_left=time_for_each_player,
                ),
            }
        else:
            players = {
                first_player_id: PlayerState(
                    chip_type=ChipType.FIRST,
                    time_left=time_for_each_player,
                ),
                second_player_id: PlayerState(
                    chip_type=ChipType.SECOND,
                    time_left=time_for_each_player,
                ),
            }

        return Game(
            id=id,
            state_id=GameStateId(uuid4()),
            status=GameStatus.NOT_STARTED,
            players=players,
            current_turn=first_player_id,
            board=[[None] * BOARD_COLUMNS for _ in range(BOARD_ROWS)],
            last_move_made_at=None,
            created_at=created_at,
        )
