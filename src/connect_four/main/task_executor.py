# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from taskiq_nats import PullBasedJetStreamBroker, NatsBroker
from dishka.integrations.taskiq import setup_dishka

from connect_four.infrastructure import load_nats_config
from connect_four.presentation.task_executor import (
    try_to_lose_on_time,
    ioc_container_factory,
)


def create_task_executor_app() -> NatsBroker:
    nats_config = load_nats_config()

    broker = PullBasedJetStreamBroker(
        [nats_config.url],
        pull_consume_timeout=0.2,
    )
    broker.register_task(try_to_lose_on_time)

    ioc_container = ioc_container_factory()
    setup_dishka(ioc_container, broker)

    return broker


task_executor = create_task_executor_app()
