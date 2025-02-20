# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

import sys
from importlib.metadata import version
from typing import Annotated

from cyclopts import App, Parameter
from faststream.cli.main import cli as run_faststream
from taskiq.cli.scheduler.run import run_scheduler_loop

from connect_four.presentation.cli import create_game, end_game
from .task_scheduler import create_task_scheduler_app


def main() -> None:
    app = create_cli_app()
    app()


def create_cli_app() -> App:
    app = App(
        name="Connect Four Game",
        version=version("connect_four"),
        help_format="rich",
    )

    app.command(create_game)
    app.command(end_game)

    app.command(run_message_consumer)
    app.command(run_task_scheduler)

    return app


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
        "connect_four.main.message_consumer:create_message_consumer_app",
        "--workers",
        workers,
        "--factory",
    ]
    run_faststream()


async def run_task_scheduler():
    """Run task scheduler."""
    task_scheduler = create_task_scheduler_app()
    await run_scheduler_loop(task_scheduler)
