# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from dataclasses import dataclass

from connect_four.domain import GameId, EndGame
from connect_four.application.common import (
    GameGateway,
    try_to_lose_by_time_task_id_factory,
    TaskScheduler,
    TransactionManager,
    GameDoesNotExistError,
)


@dataclass(frozen=True, slots=True)
class EndGameCommand:
    game_id: GameId


class EndGameProcessor:
    __slots__ = (
        "_end_game",
        "_game_gateway",
        "_task_scheduler",
        "_transaction_manager",
    )

    def __init__(
        self,
        end_game: EndGame,
        game_gateway: GameGateway,
        task_scheduler: TaskScheduler,
        transaction_manager: TransactionManager,
    ):
        self._end_game = end_game
        self._game_gateway = game_gateway
        self._task_scheduler = task_scheduler
        self._transaction_manager = transaction_manager

    async def process(self, command: EndGameCommand) -> None:
        game = await self._game_gateway.by_id(
            id=command.game_id,
            acquire=True,
        )
        if not game:
            raise GameDoesNotExistError()

        task_id = try_to_lose_by_time_task_id_factory(game.state_id)
        await self._task_scheduler.unschedule(task_id)

        self._end_game(game)
        await self._game_gateway.update(game)

        await self._transaction_manager.commit()
