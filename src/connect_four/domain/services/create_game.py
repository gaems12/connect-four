# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = (
    "Player",
    "CreateGame",
)

from datetime import datetime, timedelta
from dataclasses import dataclass
from uuid import uuid4

from connect_four.domain.identitifiers import GameId, GameStateId, UserId
from connect_four.domain.constants import (
    ChipType,
    GameStatus,
    CommunicatonType,
    BOARD_COLUMNS,
    BOARD_ROWS,
)
from connect_four.domain.models import Game, PlayerState


@dataclass(frozen=True, slots=True, kw_only=True)
class Player:
    id: UserId
    time: timedelta
    communication_type: CommunicatonType


class CreateGame:
    def __call__(
        self,
        *,
        game_id: GameId,
        first_player: Player,
        second_player: Player,
        created_at: datetime,
        last_game: Game | None = None,
    ) -> Game:
        if last_game:
            last_game_second_player = last_game.players[second_player.id]
            first_player_chip_type = last_game_second_player.chip_type

            last_game_first_player = last_game.players[first_player.id]
            second_player_chip_type = last_game_first_player.chip_type
        else:
            first_player_chip_type = ChipType.FIRST
            second_player_chip_type = ChipType.SECOND

        players = {
            first_player.id: PlayerState(
                chip_type=first_player_chip_type,
                time_left=first_player.time,
                communication_type=first_player.communication_type,
            ),
            second_player.id: PlayerState(
                chip_type=second_player_chip_type,
                time_left=second_player.time,
                communication_type=second_player.communication_type,
            ),
        }

        if first_player_chip_type == ChipType.FIRST:
            current_turn = first_player.id
        else:
            current_turn = second_player.id

        return Game(
            id=game_id,
            state_id=GameStateId(uuid4()),
            status=GameStatus.NOT_STARTED,
            players=players,
            current_turn=current_turn,
            board=[[None] * BOARD_COLUMNS for _ in range(BOARD_ROWS)],
            last_move_made_at=None,
            created_at=created_at,
        )
