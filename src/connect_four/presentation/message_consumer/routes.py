# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from typing import Final

from faststream.nats import NatsRouter, JStream, PullSub
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
    durable="connect_four.game.created",
    stream=_CONNECTION_HUB_STREAM,
    pull_sub=PullSub(timeout=0.2),
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
    durable="connect_four.game.ended",
    stream=_CONNECTION_HUB_STREAM,
    pull_sub=PullSub(timeout=0.2),
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
    durable="connect_four.game.move_was_made",
    stream=_API_GATEWAY_STREAM,
    pull_sub=PullSub(timeout=0.2),
)
@inject
async def make_move(
    *,
    command: FromDishka[MakeMoveCommand],
    command_processor: FromDishka[MakeMoveProcessor],
) -> None:
    await command_processor.process(command)
