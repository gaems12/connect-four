# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from importlib.metadata import version

from faststream import FastStream
from dishka.integrations.faststream import FastStreamProvider, setup_dishka

from connect_four.infrastructure import (
    load_nats_config,
    ioc_container_factory,
)
from connect_four.presentation.message_consumer import (
    create_broker,
    operation_id_factory,
    create_game_command_factory,
    end_game_command_factory,
    make_move_command_factory,
)


def create_message_consumer_app() -> FastStream:
    nats_config = load_nats_config()
    broker = create_broker(nats_config.url)

    app = FastStream(
        broker=broker,
        title="Four In A Row Game",
        version=version("connect_four"),
    )
    ioc_container = ioc_container_factory(
        [
            create_game_command_factory,
            end_game_command_factory,
            make_move_command_factory,
        ],
        operation_id_factory,
        FastStreamProvider(),
    )
    setup_dishka(ioc_container, app)

    return app
