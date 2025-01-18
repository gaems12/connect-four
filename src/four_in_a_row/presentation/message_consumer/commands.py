# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from faststream.nats import NatsMessage

from four_in_a_row.application import CreateGameCommand, EndGameCommand
from four_in_a_row.infrastructure import CommonRetort


async def create_game_command_factory(
    message: NatsMessage,
    common_retort: CommonRetort,
) -> CreateGameCommand:
    decoded_message = await message.decode()
    if not isinstance(decoded_message, dict):
        raise Exception()

    return common_retort.load(decoded_message, CreateGameCommand)


async def end_game_command_factory(
    message: NatsMessage,
    common_retort: CommonRetort,
) -> EndGameCommand:
    decoded_message = await message.decode()
    if not isinstance(decoded_message, dict):
        raise Exception()

    return common_retort.load(decoded_message, EndGameCommand)
