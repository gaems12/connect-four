# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from importlib.metadata import version

from faststream import FastStream
from dishka.integrations.faststream import FastStreamProvider, setup_dishka

from four_in_a_row.infrastructure import (
    nats_config_from_env,
    ioc_container_factory,
)
from four_in_a_row.presentation.message_consumer import (
    create_broker,
    create_game_command_factory,
    end_game_command_factory,
)


def create_message_consumer_app() -> FastStream:
    nats_config = nats_config_from_env()
    broker = create_broker(nats_config.url)

    app = FastStream(
        broker=broker,
        title="Four In A Row Game",
        version=version("four_in_a_row"),
    )
    ioc_container = ioc_container_factory(
        [create_game_command_factory, end_game_command_factory],
        FastStreamProvider(),
    )
    setup_dishka(ioc_container, app)

    return app
