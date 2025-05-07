# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from typing import Protocol
from enum import IntEnum, auto

from connect_four.domain import UserId, GameId, Game


class SortGamesBy(IntEnum):
    DESC_CREATED_AT = auto()


class GameGateway(Protocol):
    async def by_id(
        self,
        game_id: GameId,
        *,
        acquire: bool = False,
    ) -> Game | None:
        """
        Returns game by specified `game_id`.

        Parameters:

            `acquire`: Locks the returned game, preventing it from
                being accessed via this method with this flag until
                the current transaction is completed.
        """
        raise NotImplementedError

    async def list_by_player_ids(
        self,
        player_ids: tuple[UserId, UserId],
        *,
        sort_by: SortGamesBy | None = None,
        limit: int = 0,
    ) -> list[Game]:
        raise NotImplementedError

    async def save(self, game: Game) -> None:
        raise NotImplementedError

    async def update(self, game: Game) -> None:
        raise NotImplementedError
