# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from dataclasses import dataclass
from datetime import timedelta
from typing import Protocol
from uuid import UUID

from four_in_a_row.domain import GameId, GameStateId


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseTask:
    id: UUID
    execute_in: timedelta


@dataclass(frozen=True, slots=True, kw_only=True)
class LoseOnTimeTask(BaseTask):
    game_id: GameId
    game_state_id: GameStateId


type Task = LoseOnTimeTask


class TaskScheduler(Protocol):
    async def schedule(self, task: Task) -> None:
        raise NotImplementedError

    async def unschedule(self, task_id: UUID) -> None:
        raise NotImplementedError
