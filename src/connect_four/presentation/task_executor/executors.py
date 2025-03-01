# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from dishka.integrations.taskiq import FromDishka, inject

from connect_four.domain import GameId, GameStateId
from connect_four.application import (
    TryToLoseOnTimeCommand,
    TryToLoseOnTimeProcessor,
)
from .context_var_setter import ContextVarSetter


@inject
async def try_to_lose_on_time(
    *,
    game_id: GameId,
    game_state_id: GameStateId,
    context_var_setter: FromDishka[ContextVarSetter],
    command_processor: FromDishka[TryToLoseOnTimeProcessor],
) -> None:
    context_var_setter.set()

    command = TryToLoseOnTimeCommand(
        game_id=game_id,
        game_state_id=game_state_id,
    )
    await command_processor.process(command)
