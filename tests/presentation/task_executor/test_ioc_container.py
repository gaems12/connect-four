# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from datetime import timedelta

from connect_four.infrastructure import (
    CentrifugoConfig,
    RedisConfig,
    GameMapperConfig,
    LockManagerConfig,
    NATSConfig,
)
from connect_four.presentation.task_executor import ioc_container_factory


async def test_ioc_container(
    nats_config: NATSConfig,
    redis_config: RedisConfig,
):
    centrifugo_config = CentrifugoConfig(
        url="fake_url",
        api_key="fake_api_key",
    )
    game_mapper_config = GameMapperConfig(timedelta(hours=1))
    lock_manager_config = LockManagerConfig(timedelta(seconds=3))

    context = {
        CentrifugoConfig: centrifugo_config,
        RedisConfig: redis_config,
        GameMapperConfig: game_mapper_config,
        LockManagerConfig: lock_manager_config,
        NATSConfig: nats_config,
    }
    ioc_container_factory(context)
