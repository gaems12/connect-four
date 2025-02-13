# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

__all__ = ("ioc_container_factory",)

from typing import Any, Callable, Coroutine, Iterable

from dishka import (
    Provider,
    Scope,
    AsyncContainer,
    make_async_container,
)

from connect_four.domain import (
    CreateGame,
    EndGame,
    MakeMove,
    TryToLoseOnTime,
)
from connect_four.application import (
    GameGateway,
    EventPublisher,
    TaskScheduler,
    TransactionManager,
    IdentityProvider,
    CreateGameCommand,
    CreateGameProcessor,
    EndGameCommand,
    EndGameProcessor,
    MakeMoveCommand,
    MakeMoveProcessor,
    LoseOnTimeCommand,
    LoseOnTimeProcessor,
)
from .operation_id import OperationId
from .log import (
    LoggingConfig,
    load_logging_config,
    app_logger_factory,
    request_logger_factory,
)
from .clients import (
    httpx_client_factory,
    CentrifugoConfig,
    load_centrifugo_config,
    HTTPXCentrifugoClient,
)
from .database import (
    redis_factory,
    redis_pipeline_factory,
    GameMapperConfig,
    load_game_mapper_config,
    GameMapper,
    LockManagerConfig,
    load_lock_manager_config,
    lock_manager_factory,
    RedisTransactionManager,
)
from .message_broker import (
    NATSConfig,
    load_nats_config,
    nats_client_factory,
    nats_jetstream_factory,
    NATSEventPublisher,
)
from .scheduling import (
    taskiq_redis_schedule_source_factory,
    TaskiqTaskScheduler,
)
from .redis_config import RedisConfig, load_redis_config
from .common_retort import common_retort_factory
from .event_publisher import RealEventPublisher
from .identity_provider import NATSIdentityProvider


type _Command = (
    CreateGameCommand | EndGameCommand | MakeMoveCommand | LoseOnTimeCommand
)

type _CommandFactory = Callable[..., Coroutine[Any, Any, _Command]]
type _OperationIdFactory = Callable[..., Coroutine[Any, Any, OperationId]]


def ioc_container_factory(
    command_factories: Iterable[_CommandFactory],
    operation_id_factory: _OperationIdFactory,
    *extra_providers: Provider,
) -> AsyncContainer:
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
    provider.provide(operation_id_factory, scope=Scope.REQUEST)
    provider.provide(request_logger_factory, scope=Scope.REQUEST)

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
        NATSIdentityProvider,
        scope=Scope.REQUEST,
        provides=IdentityProvider,
    )

    provider.provide(CreateGame, scope=Scope.APP)
    provider.provide(EndGame, scope=Scope.APP)
    provider.provide(MakeMove, scope=Scope.APP)
    provider.provide(TryToLoseOnTime, scope=Scope.APP)

    for command_factory in command_factories:
        provider.provide(command_factory, scope=Scope.REQUEST)

    provider.provide(CreateGameProcessor, scope=Scope.REQUEST)
    provider.provide(EndGameProcessor, scope=Scope.REQUEST)
    provider.provide(MakeMoveProcessor, scope=Scope.REQUEST)
    provider.provide(LoseOnTimeProcessor, scope=Scope.REQUEST)

    return make_async_container(provider, *extra_providers, context=context)
