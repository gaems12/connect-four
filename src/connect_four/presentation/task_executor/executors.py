# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from dishka.integrations.taskiq import FromDishka, inject

from connect_four.application import (
    TryToLoseOnTimeCommand,
    TryToLoseOnTimeProcessor,
)


@inject
async def try_to_lose_on_time(
    *,
    command: FromDishka[TryToLoseOnTimeCommand],
    command_processor: FromDishka[TryToLoseOnTimeProcessor],
    game_id,
    game_state_id,
) -> None:
    await command_processor.process(command)
