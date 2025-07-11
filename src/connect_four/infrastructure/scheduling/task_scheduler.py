# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = ("TaskiqTaskScheduler",)

import logging
from typing import Final

from taskiq import ScheduledTask
from taskiq_redis import RedisScheduleSource

from connect_four.application import (
    TryToLoseByTimeCommand,
    TryToLoseByTimeTask,
    Task,
    TaskScheduler,
)
from connect_four.infrastructure.operation_id import OperationId


_logger: Final = logging.getLogger(__name__)


class TaskiqTaskScheduler(TaskScheduler):
    __slots__ = ("_schedule_source", "_operation_id")

    def __init__(
        self,
        schedule_source: RedisScheduleSource,
        operation_id: OperationId,
    ):
        self._schedule_source = schedule_source
        self._operation_id = operation_id

    async def schedule(self, task: Task) -> None:
        if isinstance(task, TryToLoseByTimeTask):
            await self._schedule_try_to_lose_by_time(task)

    async def _schedule_try_to_lose_by_time(
        self,
        task: TryToLoseByTimeTask,
    ) -> None:
        command = TryToLoseByTimeCommand(
            game_id=task.game_id,
            game_state_id=task.game_state_id,
        )
        schedule = ScheduledTask(
            task_name="try_to_lose_by_time",
            labels={},
            args=[self._operation_id],
            kwargs={"command": command},
            schedule_id=task.id,
            time=task.execute_at,
        )

        _logger.debug(
            {
                "message": "About to schedule a task.",
                "task": schedule.model_dump(mode="json"),
            },
        )

        await self._schedule_source.add_schedule(schedule)

    async def unschedule(self, task_id: str) -> None:
        await self._schedule_source.delete_schedule(task_id)
