# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from dishka.integrations.taskiq import FromDishka, inject

from connect_four.application import (
    TryToLoseByTimeCommand,
    TryToLoseByTimeProcessor,
)


@inject
async def try_to_lose_by_time(
    *,
    command: TryToLoseByTimeCommand,
    command_processor: FromDishka[TryToLoseByTimeProcessor],
) -> None:
    await command_processor.process(command)
