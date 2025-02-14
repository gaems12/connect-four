# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

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
    TransactionManager,
    CreateGameProcessor,
    EndGameProcessor,
)
from connect_four.infrastructure import (
    LoggingConfig,
    load_logging_config,
    app_logger_factory,
    request_logger_factory,
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
    RealEventPublisher,
    default_operation_id_factory,
)


def ioc_container_factory() -> AsyncContainer:
    provider = Provider()

    context = {
        LoggingConfig: load_logging_config(),
        CentrifugoConfig: load_centrifugo_config(),
        RedisConfig: load_redis_config(),
        GameMapperConfig: load_game_mapper_config(),
        LockManagerConfig: load_lock_manager_config(),
        NATSConfig: load_nats_config(),
    }

    provider.from_context(LoggingConfig, scope=Scope.APP)
    provider.from_context(CentrifugoConfig, scope=Scope.APP)
    provider.from_context(RedisConfig, scope=Scope.APP)
    provider.from_context(GameMapperConfig, scope=Scope.APP)
    provider.from_context(LockManagerConfig, scope=Scope.APP)
    provider.from_context(NATSConfig, scope=Scope.APP)

    provider.provide(app_logger_factory, scope=Scope.APP)
    provider.provide(default_operation_id_factory, scope=Scope.REQUEST)
    provider.provide(request_logger_factory, scope=Scope.REQUEST)

    provider.provide(httpx_client_factory, scope=Scope.APP)
    provider.provide(redis_factory, scope=Scope.APP)
    provider.provide(redis_pipeline_factory, scope=Scope.REQUEST)
    provider.provide(nats_client_factory, scope=Scope.APP)
    provider.provide(nats_jetstream_factory, scope=Scope.APP)

    provider.provide(common_retort_factory, scope=Scope.APP)

    provider.provide(lock_manager_factory, scope=Scope.REQUEST)
    provider.provide(GameMapper, provides=GameGateway, scope=Scope.REQUEST)
    provider.provide(
        RedisTransactionManager,
        provides=TransactionManager,
        scope=Scope.REQUEST,
    )

    provider.provide(NATSEventPublisher, scope=Scope.REQUEST)
    provider.provide(HTTPXCentrifugoClient, scope=Scope.REQUEST)
    provider.provide(
        RealEventPublisher,
        provides=EventPublisher,
        scope=Scope.REQUEST,
    )

    provider.provide(CreateGame, scope=Scope.APP)
    provider.provide(EndGame, scope=Scope.APP)

    provider.provide(CreateGameProcessor, scope=Scope.REQUEST)
    provider.provide(EndGameProcessor, scope=Scope.REQUEST)

    return make_async_container(provider, context=context)
