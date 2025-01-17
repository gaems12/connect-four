# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from typing import Annotated
from datetime import datetime, timedelta, timezone
from uuid import UUID

from cyclopts import Parameter, Token
import rich.prompt

from four_in_a_row.domain import GameId, UserId
from four_in_a_row.application import CreateGameCommand, CreateGameProcessor
from four_in_a_row.infrastructure import (
    str_to_timedelta,
    ioc_container_factory,
)


def _str_to_uuid(_, tokens: list[Token]) -> UUID:
    return UUID(tokens[0].value)


def _str_to_timedelta(_, tokens: list[Token]) -> timedelta:
    return str_to_timedelta(tokens[0].value)


async def create_game(
    id: Annotated[
        UUID,
        Parameter("--id", converter=_str_to_uuid),
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
        Parameter("--time-for-each-player", converter=_str_to_uuid),
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

    ioc_container = ioc_container_factory([])
    async with ioc_container() as request_container:
        command = CreateGameCommand(
            id=GameId(id),
            first_player_id=UserId(first_player_id),
            second_player_id=UserId(second_player_id),
            time_for_each_player=time_for_each_player,
            created_at=datetime.now(timezone.utc),
        )

        command_processor = await request_container.get(
            CreateGameProcessor,
        )
        await command_processor.process(command)
