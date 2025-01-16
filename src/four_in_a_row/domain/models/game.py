# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from dataclasses import dataclass
from datetime import datetime

from four_in_a_row.domain.identitifiers import GameId, GameStateId, UserId
from four_in_a_row.domain.constants import ChipType, GameStatus
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
