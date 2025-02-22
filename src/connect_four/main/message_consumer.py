# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from importlib.metadata import version

from faststream import FastStream
from dishka.integrations.faststream import setup_dishka

from connect_four.infrastructure import load_nats_config
from connect_four.presentation.message_consumer import (
    create_broker,
    ioc_container_factory,
)


def create_message_consumer_app() -> FastStream:
    nats_config = load_nats_config()
    broker = create_broker(nats_config.url)

    app = FastStream(
        broker=broker,
        title="Connect Four Game",
        version=version("connect_four"),
    )
    ioc_container = ioc_container_factory()
    setup_dishka(ioc_container, app)

    return app
