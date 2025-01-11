# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from adaptix import Retort
from faststream.nats import NatsMessage

from four_in_a_row.application import CreateGameCommand


async def create_game_command_factory(
    message: NatsMessage,
    plain_retort: Retort,
) -> CreateGameCommand:
    decoded_message = await message.decode()
    if not isinstance(decoded_message, dict):
        raise Exception()

    return plain_retort.load(decoded_message, CreateGameCommand)
