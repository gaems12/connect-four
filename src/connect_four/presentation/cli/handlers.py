# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = ("create_game", "end_game")

from typing import Annotated
from datetime import datetime, timedelta, timezone
from uuid import UUID

from cyclopts import Parameter, Token
import rich
import rich.prompt

from connect_four.domain import (
    CommunicatonType,
    GameId,
    UserId,
    LobbyId,
    Player,
)
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


def _str_to_communication_type(_, tokens: list[Token]) -> CommunicatonType:
    return CommunicatonType(tokens[0].value)


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
    first_player_time: Annotated[
        timedelta,
        Parameter("--first-player-time", converter=_str_to_timedelta),
    ],
    first_player_communication: Annotated[
        CommunicatonType,
        Parameter(
            "--first-player-communication",
            converter=_str_to_communication_type,
        ),
    ],
    second_player_id: Annotated[
        UUID,
        Parameter("--second-player-id", converter=_str_to_uuid),
    ],
    second_player_time: Annotated[
        timedelta,
        Parameter("--second-player-time", converter=_str_to_timedelta),
    ],
    second_player_communication: Annotated[
        CommunicatonType,
        Parameter(
            "--second-player-communication",
            converter=_str_to_communication_type,
        ),
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

    first_player = Player(
        id=UserId(first_player_id),
        time=first_player_time,
        communication_type=first_player_communication,
    )
    second_player = Player(
        id=UserId(second_player_id),
        time=second_player_time,
        communication_type=second_player_communication,
    )
    command = CreateGameCommand(
        game_id=GameId(game_id),
        lobby_id=LobbyId(lobby_id),
        first_player=first_player,
        second_player=second_player,
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
        f"You are going to end game {game_id.hex}. "
        "Would you like to continue?",
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
