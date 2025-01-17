# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from taskiq import TaskiqScheduler
from taskiq_nats import PushBasedJetStreamBroker
from dishka.integrations.taskiq import setup_dishka

from four_in_a_row.infrastructure import (
    nats_config_from_env,
    redis_config_from_env,
    taskiq_redis_schedule_source_factory,
    ioc_container_factory,
)


def create_task_executor_app() -> TaskiqScheduler:
    nats_config = nats_config_from_env()
    redis_config = redis_config_from_env()

    broker = PushBasedJetStreamBroker([nats_config.url])
    schedule_source = taskiq_redis_schedule_source_factory(redis_config)

    app = TaskiqScheduler(broker, [schedule_source])
    ioc_container = ioc_container_factory([])
    setup_dishka(ioc_container, app)

    return app
