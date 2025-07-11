# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = ("TryToLoseByTime",)

from datetime import timedelta

from connect_four.domain.identitifiers import GameStateId
from connect_four.domain.constants import GameStatus
from connect_four.domain.models import Game


class TryToLoseByTime:
    def __call__(
        self,
        *,
        game: Game,
        game_state_id: GameStateId,
    ) -> bool:
        """
        Ends the game with the current player's loss by time
        if possible. The method checks if the current game state id
        matches the provided one. If the state ids don't match,
        the action is not executed. Return flag indicating whether
        the game was ended.
        """
        if game.state_id != game_state_id:
            return False

        game.status = GameStatus.ENDED
        game.players[game.current_turn].time_left = timedelta(seconds=0)

        return True
