# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from dataclasses import dataclass
from datetime import datetime

from four_in_a_row.domain.identitifiers import GameId, UserId
from four_in_a_row.domain.constants import ChipType, GameStatus


@dataclass(slots=True, kw_only=True)
class Game:
    id: GameId
    status: GameStatus
    players: dict[UserId, ChipType]
    current_turn: UserId
    board: list[list[ChipType | None]]
    created_at: datetime
