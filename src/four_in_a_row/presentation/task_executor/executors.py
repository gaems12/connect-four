# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from dishka.integrations.taskiq import FromDishka, inject

from four_in_a_row.domain import GameId, GameStateId
from four_in_a_row.application import LoseOnTimeCommand, LoseOnTimeProcessor


@inject
async def lose_on_time(
    *,
    game_id: GameId,
    game_state_id: GameStateId,
    command_processor: FromDishka[LoseOnTimeProcessor],
) -> None:
    command = LoseOnTimeCommand(
        game_id=game_id,
        game_state_id=game_state_id,
    )
    await command_processor.process(command)
