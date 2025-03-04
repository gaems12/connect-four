# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

import logging

from faststream.broker.message import StreamMessage

from connect_four.application import (
    CreateGameCommand,
    EndGameCommand,
    MakeMoveCommand,
)
from connect_four.infrastructure import CommonRetort
from .context_var_setter import ContextVarSetter


_logger = logging.getLogger(__name__)


async def _process_stream_message(message: StreamMessage) -> dict:
    decoded_message = await message.decode()

    _logger.debug(
        {
            "message": "Got message from message broker.",
            "decoded_message": message,
        },
    )

    if not decoded_message or not isinstance(decoded_message, dict):
        error_message = (
            "Decoded message from message broker cannot be "
            "converted to dict.",
        )
        _logger.error(error_message)

        raise Exception(error_message)

    return decoded_message


async def create_game_command_factory(
    message: StreamMessage,
    common_retort: CommonRetort,
    context_var_setter: ContextVarSetter,
) -> CreateGameCommand:
    context_var_setter.set()
    decoded_message = await _process_stream_message(message)

    try:
        return common_retort.load(decoded_message, CreateGameCommand)
    except:
        _logger.exception(
            "Error occurred during converting decoded message "
            "from message broker to CreateGameCommand.",
        )
        raise


async def end_game_command_factory(
    message: StreamMessage,
    common_retort: CommonRetort,
    context_var_setter: ContextVarSetter,
) -> EndGameCommand:
    context_var_setter.set()
    decoded_message = await _process_stream_message(message)

    try:
        return common_retort.load(decoded_message, EndGameCommand)
    except:
        _logger.exception(
            "Error occurred during converting decoded message "
            "from message broker to EndGameCommand.",
        )
        raise


async def make_move_command_factory(
    message: StreamMessage,
    common_retort: CommonRetort,
    context_var_setter: ContextVarSetter,
) -> MakeMoveCommand:
    context_var_setter.set()
    decoded_message = await _process_stream_message(message)

    try:
        return common_retort.load(decoded_message, MakeMoveCommand)
    except:
        _logger.exception(
            "Error occurred during converting decoded message "
            "from message broker to MakeMoveCommand.",
        )
        raise
