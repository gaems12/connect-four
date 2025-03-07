# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from dataclasses import dataclass

from connect_four.domain.identitifiers import UserId
from connect_four.domain.constants import MoveRejectionReason


@dataclass(frozen=True, slots=True)
class GameStarted:
    next_turn: UserId


@dataclass(frozen=True, slots=True)
class PlayerWon: ...


@dataclass(frozen=True, slots=True)
class Draw: ...


@dataclass(frozen=True, slots=True)
class MoveAccepted:
    next_turn: UserId


@dataclass(frozen=True, slots=True)
class MoveRejected:
    reason: MoveRejectionReason


type MoveResult = GameStarted | PlayerWon | Draw | MoveAccepted | MoveRejected
