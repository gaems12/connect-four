# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from dishka import (
    Provider,
    Scope,
    AsyncContainer,
    make_async_container,
)
from dishka.integrations.taskiq import TaskiqProvider

from connect_four.domain import TryToLoseByTime
from connect_four.application import (
    GameGateway,
    EventPublisher,
    CentrifugoClient,
    TransactionManager,
    TryToLoseByTimeProcessor,
)
from connect_four.infrastructure import (
    httpx_client_factory,
    CentrifugoConfig,
    load_centrifugo_config,
    HTTPXCentrifugoClient,
    redis_factory,
    redis_pipeline_factory,
    GameMapperConfig,
    load_game_mapper_config,
    GameMapper,
    LockManagerConfig,
    load_lock_manager_config,
    lock_manager_factory,
    RedisTransactionManager,
    NATSConfig,
    load_nats_config,
    nats_client_factory,
    nats_jetstream_factory,
    NATSEventPublisher,
    RedisConfig,
    load_redis_config,
    common_retort_factory,
    get_operation_id,
)


def ioc_container_factory(context: dict | None = None) -> AsyncContainer:
    provider = Provider()

    context = context or {
        CentrifugoConfig: load_centrifugo_config(),
        RedisConfig: load_redis_config(),
        GameMapperConfig: load_game_mapper_config(),
        LockManagerConfig: load_lock_manager_config(),
        NATSConfig: load_nats_config(),
    }

    provider.from_context(CentrifugoConfig, scope=Scope.APP)
    provider.from_context(RedisConfig, scope=Scope.APP)
    provider.from_context(GameMapperConfig, scope=Scope.APP)
    provider.from_context(LockManagerConfig, scope=Scope.APP)
    provider.from_context(NATSConfig, scope=Scope.APP)

    provider.provide(get_operation_id, scope=Scope.REQUEST)
    provider.provide(common_retort_factory, scope=Scope.APP)

    provider.provide(httpx_client_factory, scope=Scope.APP)
    provider.provide(redis_factory, scope=Scope.APP)
    provider.provide(redis_pipeline_factory, scope=Scope.REQUEST)
    provider.provide(nats_client_factory, scope=Scope.APP)
    provider.provide(nats_jetstream_factory, scope=Scope.APP)

    provider.provide(lock_manager_factory, scope=Scope.REQUEST)
    provider.provide(GameMapper, scope=Scope.REQUEST, provides=GameGateway)
    provider.provide(
        RedisTransactionManager,
        scope=Scope.REQUEST,
        provides=TransactionManager,
    )

    provider.provide(
        NATSEventPublisher,
        scope=Scope.REQUEST,
        provides=EventPublisher,
    )
    provider.provide(
        HTTPXCentrifugoClient,
        scope=Scope.REQUEST,
        provides=CentrifugoClient,
    )

    provider.provide(TryToLoseByTime, scope=Scope.APP)
    provider.provide(TryToLoseByTimeProcessor, scope=Scope.REQUEST)

    return make_async_container(provider, TaskiqProvider(), context=context)
