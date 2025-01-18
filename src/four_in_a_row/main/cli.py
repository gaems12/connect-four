# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

import sys
from importlib.metadata import version
from typing import Annotated

from cyclopts import App, Parameter
from faststream.cli.main import cli as run_faststream
from taskiq.cli.scheduler.run import run_scheduler_loop
from gunicorn.app.wsgiapp import run as run_gunicorn

from four_in_a_row.presentation.cli import create_game, end_game
from .task_executor import create_task_executor_app


def main() -> None:
    app = create_cli_app()
    app()


def create_cli_app() -> App:
    app = App(
        name="Four In A Row",
        version=version("four_in_a_row"),
        help_format="rich",
    )

    app.command(create_game)
    app.command(end_game)

    app.command(run_web_api)
    app.command(run_message_consumer)
    app.command(run_task_executor)

    return app


def run_web_api(
    address: Annotated[
        str,
        Parameter("--address", show_default=True),
    ] = "0.0.0.0:8000",
    workers: Annotated[
        str,
        Parameter("--workers", show_default=True),
    ] = "1",
) -> None:
    """Run web api."""
    sys.argv = [
        "gunicorn",
        "--bind",
        address,
        "--workers",
        workers,
        "--worker-class",
        "uvicorn.workers.UvicornWorker",
        "four_in_a_row.main.web_api:create_web_api_app()",
    ]
    run_gunicorn()


def run_message_consumer(
    workers: Annotated[
        str,
        Parameter("--workers", show_default=True),
    ] = "1",
) -> None:
    """Run message consumer."""
    sys.argv = [
        "faststream",
        "run",
        "four_in_a_row.main.message_consumer:create_message_consumer_app",
        "--workers",
        workers,
        "--factory",
    ]
    run_faststream()


async def run_task_executor():
    """Run task executor."""
    task_executor = create_task_executor_app()
    await run_scheduler_loop(task_executor)
