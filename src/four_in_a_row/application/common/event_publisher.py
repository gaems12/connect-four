# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from dataclasses import dataclass
from typing import Protocol
from enum import StrEnum

from four_in_a_row.domain import (
    ChipType,
    MoveRejectionReason,
    GameId,
    UserId,
    PlayerState,
    Move,
)


class GameEndReason(StrEnum):
    WIN = "win"
    DRAW = "draw"
    TIME_IS_UP = "time_is_up"


@dataclass(frozen=True, slots=True, kw_only=True)
class GameCreatedEvent:
    game_id: GameId
    board: list[list[ChipType | None]]
    players: dict[UserId, PlayerState]
    current_turn: UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class GameStartedEvent:
    game_id: GameId


@dataclass(frozen=True, slots=True, kw_only=True)
class MoveAcceptedEvent:
    game_id: GameId
    move: Move
    players: dict[UserId, PlayerState]
    current_turn: UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class MoveRejectedEvent:
    game_id: GameId
    move: Move
    reason: MoveRejectionReason
    players: dict[UserId, PlayerState]
    current_turn: UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class GameEndedEvent:
    game_id: GameId
    move: Move | None
    players: dict[UserId, PlayerState]
    reason: GameEndReason
    last_turn: UserId


type Event = (
    GameCreatedEvent
    | GameStartedEvent
    | MoveAcceptedEvent
    | MoveRejectedEvent
    | GameEndedEvent
)


class EventPublisher(Protocol):
    async def publish(self, event: Event) -> None:
        raise NotImplementedError
