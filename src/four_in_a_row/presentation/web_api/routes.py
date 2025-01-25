# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, inject

from four_in_a_row.application import MakeMoveCommand, MakeMoveProcessor


router = APIRouter(prefix="/api/v1/internal")


@router.post("/game", tags=["centrifugo"])
@inject
async def make_move(
    *,
    command: FromDishka[MakeMoveCommand],
    command_processor: FromDishka[MakeMoveProcessor],
) -> None:
    await command_processor.process(command)
