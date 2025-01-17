# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from fastapi import Request

from four_in_a_row.application import MakeMoveCommand
from four_in_a_row.infrastructure import CommonRetort


async def make_move_command_factory(
    request: Request,
    common_retort: CommonRetort,
) -> MakeMoveCommand:
    request_json = await request.json()
    if not isinstance(request_json, dict):
        raise Exception()

    return common_retort.load(request_json, MakeMoveCommand)
