# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from dataclasses import dataclass

from connect_four.domain.identitifiers import UserId
from connect_four.domain.constants import MoveRejectionReason
from .move import Move


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseMoveResult:
    move: Move
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
