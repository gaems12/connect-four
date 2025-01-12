# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from dataclasses import dataclass

from four_in_a_row.domain.identitifiers import UserId
from four_in_a_row.domain.constants import MoveRejectionReason


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseMoveResult:
    column: int
    row: int
    player_id: UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class GameStarted(BaseMoveResult):
    next_turn: UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class PlayerWon(BaseMoveResult): ...


@dataclass(frozen=True, slots=True, kw_only=True)
class Draw(BaseMoveResult): ...


@dataclass(frozen=True, slots=True, kw_only=True)
class MoveAccepted(BaseMoveResult):
    next_turn: UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class MoveRejected(BaseMoveResult):
    reason: MoveRejectionReason


type MoveResult = GameStarted | PlayerWon | Draw | MoveAccepted | MoveRejected
