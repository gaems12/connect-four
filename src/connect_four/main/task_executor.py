# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from taskiq_nats import PushBasedJetStreamBroker, NatsBroker
from dishka.integrations.taskiq import setup_dishka

from connect_four.infrastructure import load_nats_config
from connect_four.presentation.task_executor import (
    lose_on_time,
    ioc_container_factory,
)


def create_task_executor_app() -> NatsBroker:
    nats_config = load_nats_config()

    broker = PushBasedJetStreamBroker([nats_config.url])
    broker.register_task(lose_on_time)

    ioc_container = ioc_container_factory()
    setup_dishka(ioc_container, broker)

    return broker


task_executor = create_task_executor_app()
