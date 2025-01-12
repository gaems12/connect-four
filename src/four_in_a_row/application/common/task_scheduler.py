# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from typing import Protocol


class TaskScheduler(Protocol):
    async def schedule(self) -> None:
        raise NotImplementedError
