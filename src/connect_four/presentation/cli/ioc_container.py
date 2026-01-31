# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = ("ioc_container_factory",)

from dishka import (
    Provider,
    Scope,
    AsyncContainer,
    make_async_container,
)

from connect_four.domain import CreateGame, EndGame
from connect_four.application import (
    GameGateway,
    EventPublisher,
    TaskScheduler,
    CentrifugoClient,
    TransactionManager,
    CreateGameProcessor,
    EndGameProcessor,
)
from connect_four.infrastructure import (
    httpx_client_factory,
    load_centrifugo_config,
    HTTPXCentrifugoClient,
    redis_factory,
    redis_pipeline_factory,
    load_game_mapper_config,
    GameMapper,
    load_lock_manager_config,
    lock_manager_factory,
    RedisTransactionManager,
    load_nats_config,
    nats_client_factory,
    nats_jetstream_factory,
    NATSEventPublisher,
    taskiq_redis_schedule_source_factory,
    TaskiqTaskScheduler,
    load_redis_config,
    common_retort_factory,
    get_operation_id,
)


def ioc_container_factory() -> AsyncContainer:
    provider = Provider(scope=Scope.APP)

    provider.provide(load_centrifugo_config)
    provider.provide(load_redis_config)
    provider.provide(load_game_mapper_config)
    provider.provide(load_lock_manager_config)
    provider.provide(load_nats_config)

    provider.provide(get_operation_id)
    provider.provide(common_retort_factory)

    provider.provide(httpx_client_factory)
    provider.provide(redis_factory)
    provider.provide(redis_pipeline_factory)
    provider.provide(nats_client_factory)
    provider.provide(nats_jetstream_factory)
    provider.provide(taskiq_redis_schedule_source_factory)

    provider.provide(lock_manager_factory)
    provider.provide(GameMapper, provides=GameGateway)
    provider.provide(RedisTransactionManager, provides=TransactionManager)

    provider.provide(NATSEventPublisher, provides=EventPublisher)
    provider.provide(HTTPXCentrifugoClient, provides=CentrifugoClient)
    provider.provide(TaskiqTaskScheduler, provides=TaskScheduler)

    provider.provide(CreateGame)
    provider.provide(EndGame)

    provider.provide(CreateGameProcessor)
    provider.provide(EndGameProcessor)

    return make_async_container(provider)
