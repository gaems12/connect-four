# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from datetime import datetime

from four_in_a_row.domain.identitifiers import GameId, UserId
from four_in_a_row.domain.constants import ChipType, GameStatus
from four_in_a_row.domain.models import Game


class CreateGame:
    def __call__(
        self,
        *,
        id: GameId,
        first_player_id: UserId,
        second_player_id: UserId,
        created_at: datetime,
        last_game: Game | None = None,
    ) -> Game:
        if last_game:
            players = {
                first_player_id: last_game.players[second_player_id],
                second_player_id: last_game.players[first_player_id],
            }
        else:
            players = {
                first_player_id: ChipType.FIRST,
                second_player_id: ChipType.SECOND,
            }

        return Game(
            id=id,
            status=GameStatus.NOT_STARTED,
            players=players,
            current_turn=first_player_id,
            board=[[None] * 7 for _ in range(6)],
            created_at=created_at,
        )
