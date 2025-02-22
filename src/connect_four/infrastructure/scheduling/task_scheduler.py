# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from uuid import UUID

from taskiq import ScheduledTask
from taskiq_redis import RedisScheduleSource

from connect_four.application import (
    TryToLoseOnTimeTask,
    Task,
    TaskScheduler,
)
from connect_four.infrastructure.operation_id import OperationId


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
        if isinstance(task, TryToLoseOnTimeTask):
            await self._schedule_try_to_lose_on_time(task)

    async def _schedule_try_to_lose_on_time(
        self,
        task: TryToLoseOnTimeTask,
    ) -> None:
        schedule = ScheduledTask(
            task_name="try_to_lose_on_time",
            labels={},
            args=[],
            kwargs={
                "game_id": task.game_id,
                "game_state_id": task.game_state_id,
            },
            schedule_id=task.id.hex,
            time=task.execute_at,
        )
        await self._schedule_source.add_schedule(schedule)

    async def unschedule(self, task_id: UUID) -> None:
        await self._schedule_source.delete_schedule(task_id.hex)
