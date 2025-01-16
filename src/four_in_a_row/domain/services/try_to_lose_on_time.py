# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from datetime import timedelta

from four_in_a_row.domain.identitifiers import GameStateId
from four_in_a_row.domain.constants import GameStatus
from four_in_a_row.domain.models import Game


class TryToLoseOnTime:
    def __call__(
        self,
        *,
        game: Game,
        game_state_id: GameStateId,
    ) -> bool:
        """
        Ends the game with the current player's defeat. The method
        checks if the current game state ID matches the provided one.
        If the state IDs don't match, the action is not executed.
        Return `True` if the game was successfully ended,
        `False` otherwise.
        """
        if game.state_id != game_state_id:
            return False

        game.status = GameStatus.FINISHED
        game.players[game.current_turn].time_left = timedelta(seconds=0)

        return True
