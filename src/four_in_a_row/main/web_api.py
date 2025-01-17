# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from importlib.metadata import version

from fastapi import FastAPI
from dishka.integrations.fastapi import FastapiProvider, setup_dishka

from four_in_a_row.infrastructure import ioc_container_factory
from four_in_a_row.presentation.web_api import (
    router,
    make_move_command_factory,
)


def create_web_api_app() -> FastAPI:
    app = FastAPI(
        title="Four In A Row Game",
        version=version("four_in_a_row"),
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    )
    app.include_router(router)

    ioc_container = ioc_container_factory(
        [make_move_command_factory],
        FastapiProvider(),
    )
    setup_dishka(ioc_container, app)

    return app
