# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from typing import Annotated
from datetime import datetime, timedelta, timezone
from uuid import UUID

from cyclopts import Parameter, Token
import rich
import rich.prompt

from connect_four.domain import GameId, UserId, LobbyId
from connect_four.application import (
    CreateGameCommand,
    CreateGameProcessor,
    EndGameCommand,
    EndGameProcessor,
    GameAlreadyExistsError,
    GameDoesNotExistError,
)
from connect_four.infrastructure import (
    str_to_timedelta,
    default_operation_id_factory,
    set_operation_id,
)
from .ioc_container import ioc_container_factory


def _str_to_uuid(_, tokens: list[Token]) -> UUID:
    return UUID(tokens[0].value)


def _str_to_timedelta(_, tokens: list[Token]) -> timedelta:
    return str_to_timedelta(tokens[0].value)


async def create_game(
    game_id: Annotated[
        UUID,
        Parameter("--id", converter=_str_to_uuid),
    ],
    lobby_id: Annotated[
        UUID,
        Parameter("--lobby-id", converter=_str_to_uuid),
    ],
    first_player_id: Annotated[
        UUID,
        Parameter("--first-player-id", converter=_str_to_uuid),
    ],
    second_player_id: Annotated[
        UUID,
        Parameter("--second-player-id", converter=_str_to_uuid),
    ],
    time_for_each_player: Annotated[
        timedelta,
        Parameter("--time-for-each-player", converter=_str_to_timedelta),
    ],
) -> None:
    """
    Creates a new game. Asks confirmation before exection.
    """
    execution_is_confirmed = rich.prompt.Confirm.ask(
        "You are going to create a new game. Would you like to continue?",
    )
    if not execution_is_confirmed:
        return

    ioc_container = ioc_container_factory()

    operation_id = default_operation_id_factory()
    set_operation_id(operation_id)

    command = CreateGameCommand(
        game_id=GameId(game_id),
        lobby_id=LobbyId(lobby_id),
        first_player_id=UserId(first_player_id),
        second_player_id=UserId(second_player_id),
        time_for_each_player=time_for_each_player,
        created_at=datetime.now(timezone.utc),
    )
    command_processor = await ioc_container.get(CreateGameProcessor)

    try:
        await command_processor.process(command)
    except GameAlreadyExistsError:
        rich.print("Game already exists.")


async def end_game(
    game_id: Annotated[
        UUID,
        Parameter("--id", converter=_str_to_uuid),
    ],
) -> None:
    """
    Ends game. Asks confirmation before exection.
    """
    execution_is_confirmed = rich.prompt.Confirm.ask(
        f"You are going to end game {game_id.hex}. Would you like to continue?",
    )
    if not execution_is_confirmed:
        return

    ioc_container = ioc_container_factory()

    operation_id = default_operation_id_factory()
    set_operation_id(operation_id)

    command = EndGameCommand(GameId(game_id))
    command_processor = await ioc_container.get(EndGameProcessor)

    try:
        await command_processor.process(command)
    except GameDoesNotExistError:
        rich.print("Game doesn't exist.")
