# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from typing import Final

from faststream.nats import NatsRouter, JStream
from dishka.integrations.faststream import FromDishka, inject

from four_in_a_row.application import (
    CreateGameCommand,
    CreateGameProcessor,
    EndGameCommand,
    EndGameProcessor,
    MakeMoveCommand,
    MakeMoveProcessor,
)


_CONNECTION_HUB_STREAM: Final = JStream("connection_hub")
_API_GATEWAY_STREAM: Final = JStream("api_gateway")

router = NatsRouter()


@router.subscriber(
    subject="game.created",
    queue="four_in_a_row.game.created",
    durable="four_in_a_row.game.created",
    stream=_CONNECTION_HUB_STREAM,
)
@inject
async def create_game(
    *,
    command: FromDishka[CreateGameCommand],
    command_processor: FromDishka[CreateGameProcessor],
) -> None:
    await command_processor.process(command)


@router.subscriber(
    subject="game.ended",
    queue="four_in_a_row.game.ended",
    durable="four_in_a_row.game.ended",
    stream=_CONNECTION_HUB_STREAM,
)
@inject
async def end_game(
    *,
    command: FromDishka[EndGameCommand],
    command_processor: FromDishka[EndGameProcessor],
) -> None:
    await command_processor.process(command)


@router.subscriber(
    subject="game.move_was_made",
    queue="four_in_a_row.game.move_was_made",
    durable="four_in_a_row.game.move_was_made",
    stream=_API_GATEWAY_STREAM,
)
@inject
async def make_move(
    *,
    command: FromDishka[MakeMoveCommand],
    command_processor: FromDishka[MakeMoveProcessor],
) -> None:
    await command_processor.process(command)
