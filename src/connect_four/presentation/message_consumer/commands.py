# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

import logging

from faststream.broker.message import StreamMessage

from connect_four.application import (
    CreateGameCommand,
    EndGameCommand,
    MakeMoveCommand,
)
from connect_four.infrastructure import CommonRetort


_logger = logging.getLogger(__name__)


async def create_game_command_factory(
    message: StreamMessage,
    common_retort: CommonRetort,
) -> CreateGameCommand:
    decoded_message = await message.decode()

    _logger.debug(
        {
            "message": "Got message from message broker.",
            "decoded_message": message,
        },
    )

    if not decoded_message or not isinstance(decoded_message, dict):
        error_message = "StreamMessage cannot be converted to dict."
        _logger.error(error_message)

        raise Exception(error_message)

    return common_retort.load(decoded_message, CreateGameCommand)


async def end_game_command_factory(
    message: StreamMessage,
    common_retort: CommonRetort,
) -> EndGameCommand:
    decoded_message = await message.decode()

    _logger.debug(
        {
            "message": "Got message from message broker.",
            "decoded_message": message,
        },
    )

    if not decoded_message or not isinstance(decoded_message, dict):
        error_message = "StreamMessage cannot be converted to dict."
        _logger.error(error_message)

        raise Exception(error_message)

    return common_retort.load(decoded_message, EndGameCommand)


async def make_move_command_factory(
    message: StreamMessage,
    common_retort: CommonRetort,
) -> MakeMoveCommand:
    decoded_message = await message.decode()

    _logger.debug(
        {
            "message": "Got message from message broker.",
            "decoded_message": message,
        },
    )

    if not decoded_message or not isinstance(decoded_message, dict):
        error_message = "StreamMessage cannot be converted to dict."
        _logger.error(error_message)

        raise Exception(error_message)

    return common_retort.load(decoded_message, MakeMoveCommand)
