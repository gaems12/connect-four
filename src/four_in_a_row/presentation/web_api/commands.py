# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from fastapi import Request

from four_in_a_row.application import MakeMoveCommand
from four_in_a_row.infrastructure import CommonRetort


async def make_move_command_factory(
    request: Request,
    common_retort: CommonRetort,
) -> MakeMoveCommand:
    game_id = request.path_params.get("game_id")
    if not game_id:
        raise Exception("HTTP request's URL has no 'game_id' path param.")

    request_json = await request.json()
    if not request_json or not isinstance(request_json, dict):
        raise Exception("HTTP request's JSON cannot be converted to dict.")

    command_as_dict = {"game_id": game_id, **request_json}
    return common_retort.load(command_as_dict, MakeMoveCommand)
