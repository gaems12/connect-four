# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from typing import Final

from faststream.nats import NatsRouter, JStream
from dishka.integrations.faststream import FromDishka, inject

from connect_four.application import (
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
    queue="connect_four.game.created",
    durable="connect_four.game.created",
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
    queue="connect_four.game.ended",
    durable="connect_four.game.ended",
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
    queue="connect_four.game.move_was_made",
    durable="connect_four.game.move_was_made",
    stream=_API_GATEWAY_STREAM,
)
@inject
async def make_move(
    *,
    command: FromDishka[MakeMoveCommand],
    command_processor: FromDishka[MakeMoveProcessor],
) -> None:
    await command_processor.process(command)
