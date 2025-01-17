# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from faststream.nats import NatsRouter
from dishka.integrations.faststream import FromDishka, inject

from four_in_a_row.application import CreateGameCommand, CreateGameProcessor


router = NatsRouter()


@router.subscriber("game.created", "four_in_a_row")
@inject
async def create_game(
    *,
    command: FromDishka[CreateGameCommand],
    command_processor: FromDishka[CreateGameProcessor],
) -> None:
    await command_processor.process(command)
