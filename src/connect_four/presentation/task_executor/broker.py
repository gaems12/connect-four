# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = ("create_broker",)

from typing import overload

from taskiq import InMemoryBroker, SimpleRetryMiddleware
from taskiq_nats import PullBasedJetStreamBroker

from .executors import try_to_lose_by_time
from .middlewares import OperationIdMiddleware, LoggingMiddleware


@overload
def create_broker() -> InMemoryBroker: ...


@overload
def create_broker(nats_url: str) -> PullBasedJetStreamBroker: ...


def create_broker(
    nats_url: str | None = None,
) -> InMemoryBroker | PullBasedJetStreamBroker:
    """
    Creates a TaskIQ broker, either using NATS JetStream or an
    in-memory broker. If a `nats_url` is provided, a Pull-Based
    JetStream broker is created. Otherwise, an in-memory broker
    is used.
    """
    broker: InMemoryBroker | PullBasedJetStreamBroker

    if nats_url:
        broker = PullBasedJetStreamBroker(
            [nats_url],
            pull_consume_timeout=0.2,
        )
    else:
        broker = InMemoryBroker()

    broker.add_middlewares(
        OperationIdMiddleware(),
        LoggingMiddleware(),
        SimpleRetryMiddleware(),
    )
    broker.register_task(
        try_to_lose_by_time,
        task_name="try_to_lose_by_time",
        retry_on_error=True,
        max_retries=5,
    )

    return broker
