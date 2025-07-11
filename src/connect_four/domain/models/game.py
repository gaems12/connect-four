# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = ("Game",)

from dataclasses import dataclass
from datetime import datetime

from connect_four.domain.identitifiers import GameId, GameStateId, UserId
from connect_four.domain.constants import ChipType, GameStatus
from .player_state import PlayerState


@dataclass(slots=True, kw_only=True)
class Game:
    id: GameId
    state_id: GameStateId
    status: GameStatus
    players: dict[UserId, PlayerState]
    current_turn: UserId
    board: list[list[ChipType | None]]
    last_move_made_at: datetime | None
    created_at: datetime
