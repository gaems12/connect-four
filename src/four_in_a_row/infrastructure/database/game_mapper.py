# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

import json
from dataclasses import dataclass
from datetime import timedelta
from typing import Iterable

from redis.asyncio.client import Redis, Pipeline
from adaptix import Retort

from four_in_a_row.domain import GameId, UserId, Game
from four_in_a_row.application import SortGamesBy, GameGateway
from four_in_a_row.infrastructure.utils import (
    get_env_var,
    str_to_timedelta,
)
from .lock_manager import LockManager


def game_mapper_config_from_env() -> "GameMapperConfig":
    return GameMapperConfig(
        game_expires_in=get_env_var(
            key="GAME_MAPPER_GAME_EXPIRES_IN",
            value_factory=str_to_timedelta,
        ),
    )


@dataclass(frozen=True, slots=True)
class GameMapperConfig:
    game_expires_in: timedelta


class GameMapper(GameGateway):
    __slots__ = (
        "_redis",
        "_redis_pipeline",
        "_plain_retort",
        "_lock_manager",
        "_config",
    )

    def __init__(
        self,
        redis: Redis,
        redis_pipeline: Pipeline,
        plain_retort: Retort,
        lock_manager: LockManager,
        config: GameMapperConfig,
    ):
        self._redis = redis
        self._redis_pipeline = redis_pipeline
        self._plain_retort = plain_retort
        self._lock_manager = lock_manager
        self._config = config

    async def by_id(
        self,
        id: GameId,
        *,
        acquire: bool = False,
    ) -> Game | None:
        if acquire:
            lock_id = self._lock_id_factory(id)
            await self._lock_manager.acquire(lock_id)

        pattern = self._pattern_to_find_game_by_id(id)
        keys = await self._redis.keys(pattern)
        if not keys:
            return None

        game_as_json = await self._redis.get(keys[0])  # type: ignore
        if game_as_json:
            game_as_dict = json.loads(game_as_json)
            return self._plain_retort.load(game_as_dict, Game)

        return None

    async def list_by_player_ids(
        self,
        player_ids: tuple[UserId, UserId],
        *,
        sort_by: SortGamesBy | None = None,
        limit: int = 0,
    ) -> list[Game]:
        pattern = self._pattern_to_find_game_by_player_ids(player_ids)
        keys = await self._redis.keys(pattern)
        if not keys:
            return []

        games = []
        game_count = 0

        for key in keys:
            if game_count == limit:
                break

            game_as_json = await self._redis.get(key)  # type: ignore
            if not game_as_json:
                continue

            game_as_dict = json.loads(game_as_json)
            game = self._plain_retort.load(game_as_dict, Game)
            games.append(game)

            game_count += 1

        if not sort_by:
            return games

        return sorted(games, key=lambda game: game.created_at, reverse=True)

    async def save(self, game: Game) -> None:
        game_key = self._game_key_factory(
            game_id=game.id,
            player_ids=game.players.keys(),
        )

        game_as_dict = self._plain_retort.dump(game, dict)
        game_as_json = json.dumps(game_as_dict)

        self._redis_pipeline.set(
            name=game_key,
            value=game_as_json,
            ex=self._config.game_expires_in,
        )

    async def update(self, game: Game) -> None:
        game_key = self._game_key_factory(
            game_id=game.id,
            player_ids=game.players.keys(),
        )

        game_as_dict = self._plain_retort.dump(game, dict)
        game_as_json = json.dumps(game_as_dict)

        self._redis_pipeline.set(game_key, game_as_json)

    def _game_key_factory(
        self,
        *,
        game_id: GameId,
        player_ids: Iterable[UserId],
    ) -> str:
        sorted_player_ids = sorted(player_ids)
        return (
            f"games:id:{game_id.hex}:player_ids:"
            f"{sorted_player_ids[0].hex}:{sorted_player_ids[1].hex}"
        )

    def _pattern_to_find_game_by_id(self, game_id: GameId) -> str:
        return f"games:id:{game_id.hex}:player_ids:*"

    def _pattern_to_find_game_by_player_ids(
        self,
        player_ids: Iterable[UserId],
    ) -> str:
        sorted_player_ids = sorted(player_ids)
        return (
            "games:id:*:player_ids:"
            f"{sorted_player_ids[0].hex}:{sorted_player_ids[1].hex}"
        )

    def _lock_id_factory(self, game_id: GameId) -> str:
        return f"games:id:{game_id.hex}"
