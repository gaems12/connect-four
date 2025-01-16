# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from taskiq import TaskiqScheduler
from taskiq_nats import PushBasedJetStreamBroker

from four_in_a_row.infrastructure import (
    nats_config_from_env,
    redis_config_from_env,
    taskiq_redis_schedule_source_factory,
)


def create_task_executor_app() -> TaskiqScheduler:
    nats_config = nats_config_from_env()
    redis_config = redis_config_from_env()

    broker = PushBasedJetStreamBroker([nats_config.url])
    schedule_source = taskiq_redis_schedule_source_factory(redis_config)

    return TaskiqScheduler(broker, [schedule_source])
