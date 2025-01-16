# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from uuid import UUID

from taskiq import ScheduledTask
from taskiq_redis import RedisScheduleSource

from four_in_a_row.application import (
    LoseOnTimeTask,
    Task,
    TaskScheduler,
)


class TaskiqTaskScheduler(TaskScheduler):
    __slots__ = ("schedule_source",)

    def __init__(self, schedule_source: RedisScheduleSource):
        self._schedule_source = schedule_source

    async def schedule(self, task: Task) -> None:
        if isinstance(task, LoseOnTimeTask):
            await self._schedule_lose_on_time(task)

    async def _schedule_lose_on_time(
        self,
        task: LoseOnTimeTask,
    ) -> None:
        schedule = ScheduledTask(
            task_name="lose_on_time",
            labels={},
            kwargs={
                "game_id": task.game_id,
                "game_state_id": task.game_state_id,
            },
            schedule_id=task.id.hex,
            time=task.execute_in,
        )
        await self._schedule_source.add_schedule(schedule)

    async def unschedule(self, task_id: UUID) -> None:
        await self._schedule_source.delete_schedule(task_id.hex)
