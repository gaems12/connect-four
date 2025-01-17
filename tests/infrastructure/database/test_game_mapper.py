# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from typing import AsyncGenerator, Final
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import pytest
from redis.asyncio.client import Redis, Pipeline
from uuid_extensions import uuid7

from four_in_a_row.domain import (
    GameId,
    GameStateId,
    UserId,
    BOARD_ROWS,
    BOARD_COLUMNS,
    ChipType,
    GameStatus,
    PlayerState,
    Game,
)
from four_in_a_row.application import SortGamesBy
from four_in_a_row.infrastructure import (
    get_env_var,
    RedisConfig,
    redis_factory,
    redis_pipeline_factory,
    common_retort_factory,
    LockManagerConfig,
    LockManager,
    GameMapperConfig,
    GameMapper,
    RedisTransactionManager,
)


_PLAYER_1_ID: Final = UserId(uuid7())
_PLAYER_2_ID: Final = UserId(uuid7())


@pytest.fixture(scope="function")
async def redis() -> AsyncGenerator[Redis, None]:
    redis_url = get_env_var("TEST_REDIS_URL")
    redis_config = RedisConfig(url=redis_url)

    ctx_manager = asynccontextmanager(redis_factory)
    async with ctx_manager(redis_config) as redis:
        yield redis


@pytest.fixture(scope="function")
async def redis_pipeline(redis: Redis) -> AsyncGenerator[Pipeline, None]:
    ctx_manager = asynccontextmanager(redis_pipeline_factory)
    async with ctx_manager(redis) as redis_pipeline:
        yield redis_pipeline


async def test_game_mapper(redis: Redis, redis_pipeline: Pipeline):
    lock_manager_config = LockManagerConfig(timedelta(minutes=1))
    lock_manager = LockManager(
        redis=redis,
        config=lock_manager_config,
    )

    game_mapper_config = GameMapperConfig(timedelta(days=1))
    game_mapper = GameMapper(
        redis=redis,
        redis_pipeline=redis_pipeline,
        common_retort=common_retort_factory(),
        lock_manager=lock_manager,
        config=game_mapper_config,
    )

    transaction_manager = RedisTransactionManager(
        redis_pipeline=redis_pipeline,
        lock_manager=lock_manager,
    )

    game = await game_mapper.by_id(GameId(uuid7()))
    assert game == None

    game_id = GameId(uuid7())
    players = {
        _PLAYER_1_ID: PlayerState(
            chip_type=ChipType.FIRST,
            time_left=timedelta(minutes=1),
        ),
        _PLAYER_2_ID: PlayerState(
            chip_type=ChipType.SECOND,
            time_left=timedelta(minutes=1),
        ),
    }

    new_game = Game(
        id=game_id,
        state_id=GameStateId(uuid7()),
        status=GameStatus.NOT_STARTED,
        players=players,
        current_turn=_PLAYER_1_ID,
        board=[[None] * BOARD_COLUMNS for _ in range(BOARD_ROWS)],
        last_move_made_at=None,
        created_at=datetime.now(timezone.utc),
    )
    await game_mapper.save(new_game)
    await transaction_manager.commit()

    game_from_database = await game_mapper.by_id(
        game_id,
        acquire=True,
    )
    assert game_from_database == new_game

    updated_game = game_from_database
    updated_game.status = GameStatus.ENDED
    await game_mapper.update(updated_game)
    await transaction_manager.commit()

    game_from_database = await game_mapper.by_id(game_id)
    assert game_from_database == updated_game

    games = await game_mapper.list_by_player_ids(
        player_ids=(_PLAYER_1_ID, _PLAYER_2_ID),
        sort_by=SortGamesBy.DESC_CREATED_AT,
        limit=0,
    )
    assert games == [updated_game]
