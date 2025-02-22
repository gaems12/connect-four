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
from .context_var_setter import ContextVarSetter


_CONNECTION_HUB_STREAM: Final = JStream("connection_hub")
_API_GATEWAY_STREAM: Final = JStream("api_gateway")

router = NatsRouter()


@router.subscriber(
    subject="game.created",
    durable="connect_four_game_created",
    stream=_CONNECTION_HUB_STREAM,
    pull_sub=PullSub(timeout=0.2),
)
@inject
async def create_game(
    *,
    command: FromDishka[CreateGameCommand],
    command_processor: FromDishka[CreateGameProcessor],
    context_var_setter: FromDishka[ContextVarSetter],
) -> None:
    await context_var_setter.set()
    await command_processor.process(command)


@router.subscriber(
    subject="game.ended",
    durable="connect_four_game_ended",
    stream=_CONNECTION_HUB_STREAM,
    pull_sub=PullSub(timeout=0.2),
)
@inject
async def end_game(
    *,
    command: FromDishka[EndGameCommand],
    command_processor: FromDishka[EndGameProcessor],
    context_var_setter: FromDishka[ContextVarSetter],
) -> None:
    await context_var_setter.set()
    await command_processor.process(command)


@router.subscriber(
    subject="game.move_was_made",
    durable="connect_four_game_move_was_made",
    stream=_API_GATEWAY_STREAM,
    pull_sub=PullSub(timeout=0.2),
)
@inject
async def make_move(
    *,
    command: FromDishka[MakeMoveCommand],
    command_processor: FromDishka[MakeMoveProcessor],
    context_var_setter: FromDishka[ContextVarSetter],
) -> None:
    await context_var_setter.set()
    await command_processor.process(command)
