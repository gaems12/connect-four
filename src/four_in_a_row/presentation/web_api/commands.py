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
    if not request_json or not isinstance(request_json, dict):
        raise Exception("HTTP request's JSON cannot be converted to dict.")

    return common_retort.load(request_json, MakeMoveCommand)
