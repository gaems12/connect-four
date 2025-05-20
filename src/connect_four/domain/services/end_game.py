# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = ("EndGame",)

from uuid import uuid4

from connect_four.domain.identitifiers import GameStateId
from connect_four.domain.constants import GameStatus
from connect_four.domain.models import Game


class EndGame:
    def __call__(self, game: Game) -> None:
        game.state_id = GameStateId(uuid4())
        game.status = GameStatus.ENDED
