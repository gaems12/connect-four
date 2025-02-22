# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from dishka import (
    Provider,
    Scope,
    AsyncContainer,
    make_async_container,
)
from dishka.integrations.faststream import FastStreamProvider

from connect_four.domain import (
    CreateGame,
    EndGame,
    MakeMove,
)
from connect_four.application import (
    GameGateway,
    EventPublisher,
    TaskScheduler,
    TransactionManager,
    IdentityProvider,
    CreateGameProcessor,
    EndGameProcessor,
    MakeMoveProcessor,
)
from connect_four.infrastructure import (
    LoggingConfig,
    load_logging_config,
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
    taskiq_redis_schedule_source_factory,
    TaskiqTaskScheduler,
    RedisConfig,
    load_redis_config,
    common_retort_factory,
    RealEventPublisher,
)
from .commands import (
    create_game_command_factory,
    end_game_command_factory,
    make_move_command_factory,
)
from .identity_provider import MessageBrokerIdentityProvider
from .context_var_setter import ContextVarSetter
from .operation_id import operation_id_factory


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

    provider.provide(operation_id_factory, scope=Scope.REQUEST)
    provider.provide(ContextVarSetter, scope=Scope.REQUEST)

    provider.provide(httpx_client_factory, scope=Scope.APP)
    provider.provide(redis_factory, scope=Scope.APP)
    provider.provide(redis_pipeline_factory, scope=Scope.REQUEST)
    provider.provide(nats_client_factory, scope=Scope.APP)
    provider.provide(nats_jetstream_factory, scope=Scope.APP)
    provider.provide(taskiq_redis_schedule_source_factory, scope=Scope.APP)

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

    provider.provide(
        TaskiqTaskScheduler,
        scope=Scope.REQUEST,
        provides=TaskScheduler,
    )

    provider.provide(
        MessageBrokerIdentityProvider,
        scope=Scope.REQUEST,
        provides=IdentityProvider,
    )

    provider.provide(CreateGame, scope=Scope.APP)
    provider.provide(EndGame, scope=Scope.APP)
    provider.provide(MakeMove, scope=Scope.APP)

    provider.provide(create_game_command_factory, scope=Scope.REQUEST)
    provider.provide(end_game_command_factory, scope=Scope.REQUEST)
    provider.provide(make_move_command_factory, scope=Scope.REQUEST)

    provider.provide(CreateGameProcessor, scope=Scope.REQUEST)
    provider.provide(EndGameProcessor, scope=Scope.REQUEST)
    provider.provide(MakeMoveProcessor, scope=Scope.REQUEST)

    return make_async_container(
        provider,
        FastStreamProvider(),
        context=context,
    )
