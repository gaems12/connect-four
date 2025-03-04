# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

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


_STREAM: Final = JStream(name="games", declare=False)

router = NatsRouter()


@router.subscriber(
    subject="connection_hub.connect_four.game.created",
    durable="connect_four_game_created",
    stream=_STREAM,
    pull_sub=PullSub(timeout=0.2),
)
@inject
async def create_game(
    *,
    command: CreateGameCommand,
    command_processor: FromDishka[CreateGameProcessor],
) -> None:
    await command_processor.process(command)


@router.subscriber(
    subject="connection_hub.connect_four.game.player_disqualified",
    durable="connect_four_game_player_disqualified",
    stream=_STREAM,
    pull_sub=PullSub(timeout=0.2),
)
@inject
async def end_game(
    *,
    command: EndGameCommand,
    command_processor: FromDishka[EndGameProcessor],
) -> None:
    await command_processor.process(command)


@router.subscriber(
    subject="api_gateway.connect_four.game.move_was_made",
    durable="connect_four_game_move_was_made",
    stream=_STREAM,
    pull_sub=PullSub(timeout=0.2),
)
@inject
async def make_move(
    *,
    command: MakeMoveCommand,
    command_processor: FromDishka[MakeMoveProcessor],
) -> None:
    await command_processor.process(command)
