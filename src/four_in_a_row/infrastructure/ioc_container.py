# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

__all__ = ("ioc_container_factory",)

from typing import Callable, Iterable

from dishka import Provider, Scope, AsyncContainer, make_async_container
from adaptix import Retort

from four_in_a_row.application import (
    GameGateway,
    EventPublisher,
    TransactionManager,
    CreateGameCommand,
    CreateGameProcessor,
)
from .clients import (
    httpx_client_factory,
    CentrifugoConfig,
    centrifugo_config_from_env,
    HTTPXCentrifugoClient,
)
from .database import (
    RedisConfig,
    redis_config_from_env,
    redis_factory,
    redis_pipeline_factory,
    GameMapperConfig,
    game_mapper_config_from_env,
    GameMapper,
    LockManagerConfig,
    lock_manager_config_from_env,
    LockManager,
    RedisTransactionManager,
)
from .message_borker import (
    NATSConfig,
    nats_config_from_env,
    nats_client_factory,
    nats_jetstream_factory,
    NATSEventPublisher,
)
from .event_publisher import RealEventPublisher


type Command = CreateGameCommand


def ioc_container_factory(
    command_factories: Iterable[Callable[..., Command]],
    *extra_providers: Provider,
) -> AsyncContainer:
    provider = Provider()

    context = {
        CentrifugoConfig: centrifugo_config_from_env(),
        RedisConfig: redis_config_from_env(),
        GameMapperConfig: game_mapper_config_from_env(),
        LockManagerConfig: lock_manager_config_from_env(),
        NATSConfig: nats_config_from_env(),
    }

    provider.from_context(CentrifugoConfig, scope=Scope.APP)
    provider.from_context(RedisConfig, scope=Scope.APP)
    provider.from_context(GameMapperConfig, scope=Scope.APP)
    provider.from_context(LockManagerConfig, scope=Scope.APP)
    provider.from_context(NATSConfig, scope=Scope.APP)

    provider.provide(httpx_client_factory, scope=Scope.APP)
    provider.provide(redis_factory, scope=Scope.APP)
    provider.provide(redis_pipeline_factory, scope=Scope.REQUEST)
    provider.provide(nats_client_factory, scope=Scope.APP)
    provider.provide(nats_jetstream_factory, scope=Scope.APP)

    provider.provide(Retort, scope=Scope.APP)

    provider.provide(LockManager, scope=Scope.REQUEST)
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

    for command_factory in command_factories:
        provider.provide(command_factory, scope=Scope.REQUEST)

    provider.provide(CreateGameProcessor, scope=Scope.REQUEST)

    return make_async_container(provider, *extra_providers, context=context)
