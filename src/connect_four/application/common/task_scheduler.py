# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from connect_four.domain import GameId, GameStateId


def try_to_lose_by_time_task_id_factory(
    game_state_id: GameStateId,
) -> str:
    return f"try_to_lose_by_time:{game_state_id.hex}"


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseTask:
    id: str
    execute_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class TryToLoseByTimeTask(BaseTask):
    game_id: GameId
    game_state_id: GameStateId


type Task = TryToLoseByTimeTask


class TaskScheduler(Protocol):
    async def schedule(self, task: Task) -> None:
        raise NotImplementedError

    async def unschedule(self, task_id: str) -> None:
        raise NotImplementedError
