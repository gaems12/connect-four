# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from uuid import uuid4

from four_in_a_row.domain.identitifiers import GameStateId
from four_in_a_row.domain.constants import GameStatus
from four_in_a_row.domain.models import Game


class EndGame:
    def __call__(self, game: Game) -> None:
        game.state_id = GameStateId(uuid4())
        game.status = GameStatus.ENDED
