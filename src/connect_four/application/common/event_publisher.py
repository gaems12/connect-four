# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = (
    "GameEndReason",
    "GameCreatedEvent",
    "MoveAcceptedEvent",
    "MoveRejectedEvent",
    "GameEndedEvent",
    "Event",
    "EventPublisher",
)

from dataclasses import dataclass
from typing import Protocol
from enum import StrEnum

from connect_four.domain import (
    ChipType,
    MoveRejectionReason,
    GameId,
    UserId,
    LobbyId,
    PlayerState,
    ChipLocation,
)


class GameEndReason(StrEnum):
    WIN = "win"
    DRAW = "draw"
    LOSS_BY_TIME = "loss_by_time"


@dataclass(frozen=True, slots=True, kw_only=True)
class GameCreatedEvent:
    game_id: GameId
    lobby_id: LobbyId
    board: list[list[ChipType | None]]
    players: dict[UserId, PlayerState]
    current_turn: UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class MoveAcceptedEvent:
    game_id: GameId
    chip_location: ChipLocation
    players: dict[UserId, PlayerState]
    current_turn: UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class MoveRejectedEvent:
    game_id: GameId
    reason: MoveRejectionReason
    players: dict[UserId, PlayerState]
    current_turn: UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class GameEndedEvent:
    game_id: GameId
    chip_location: ChipLocation | None
    players: dict[UserId, PlayerState]
    reason: GameEndReason
    last_turn: UserId


type Event = (
    GameCreatedEvent | MoveAcceptedEvent | MoveRejectedEvent | GameEndedEvent
)


class EventPublisher(Protocol):
    async def publish(self, event: Event) -> None:
        raise NotImplementedError
