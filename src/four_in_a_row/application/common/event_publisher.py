# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from dataclasses import dataclass
from typing import Protocol

from four_in_a_row.domain import GameId, UserId, PlayerState


@dataclass(frozen=True, slots=True, kw_only=True)
class GameCreatedEvent:
    id: GameId
    players: dict[UserId, PlayerState]
    current_turn: UserId


type Event = GameCreatedEvent


class EventPublisher(Protocol):
    async def publish(self, event: Event) -> None:
        raise NotImplementedError
