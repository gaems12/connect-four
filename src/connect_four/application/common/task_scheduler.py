# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from connect_four.domain import GameId, GameStateId


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseTask:
    id: UUID
    execute_at: datetime


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
