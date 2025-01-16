# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from uuid import UUID

from taskiq import ScheduledTask
from taskiq_redis import RedisScheduleSource

from four_in_a_row.application import (
    NotifyOnTimeIsUpTask,
    Task,
    TaskScheduler,
)


class TaskiqTaskScheduler(TaskScheduler):
    __slots__ = ("schedule_source",)

    def __init__(self, schedule_source: RedisScheduleSource):
        self._schedule_source = schedule_source

    async def schedule(self, task: Task) -> None:
        if isinstance(task, NotifyOnTimeIsUpTask):
            await self._schedule_notify_on_time_is_up(task)

    async def _schedule_notify_on_time_is_up(
        self,
        task: NotifyOnTimeIsUpTask,
    ) -> None:
        schedule = ScheduledTask(
            task_name="notify_on_time_is_up",
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
