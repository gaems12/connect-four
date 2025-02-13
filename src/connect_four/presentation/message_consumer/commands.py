# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from faststream.broker.message import StreamMessage

from connect_four.application import (
    CreateGameCommand,
    EndGameCommand,
    MakeMoveCommand,
)
from connect_four.infrastructure import CommonRetort


async def create_game_command_factory(
    message: StreamMessage,
    common_retort: CommonRetort,
) -> CreateGameCommand:
    decoded_message = await message.decode()
    if not decoded_message or not isinstance(decoded_message, dict):
        raise Exception("StreamMessage cannot be converted to dict.")

    return common_retort.load(decoded_message, CreateGameCommand)


async def end_game_command_factory(
    message: StreamMessage,
    common_retort: CommonRetort,
) -> EndGameCommand:
    decoded_message = await message.decode()
    if not decoded_message or not isinstance(decoded_message, dict):
        raise Exception("StreamMessage cannot be converted to dict.")

    return common_retort.load(decoded_message, EndGameCommand)


async def make_move_command_factory(
    message: StreamMessage,
    common_retort: CommonRetort,
) -> MakeMoveCommand:
    decoded_message = await message.decode()
    if not decoded_message or not isinstance(decoded_message, dict):
        raise Exception("StreamMessage cannot be converted to dict.")

    return common_retort.load(decoded_message, MakeMoveCommand)
