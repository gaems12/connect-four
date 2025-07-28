# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

import sys
from importlib.metadata import version
from typing import Annotated

from cyclopts import App, Parameter
from faststream.cli.main import cli as run_faststream
from taskiq.cli.scheduler.run import run_scheduler_loop
from taskiq.cli.worker.args import WorkerArgs
from taskiq.cli.worker.run import run_worker

from connect_four.infrastructure import (
    setup_logging,
    NATSConfig,
    nats_client_factory,
    nats_jetstream_factory,
    NATSStreamCreator,
)
from connect_four.presentation.cli import create_game, end_game
from .task_scheduler import create_task_scheduler_app


def main() -> None:
    setup_logging()
    app = create_cli_app()
    app()


def create_cli_app() -> App:
    app = App(
        name="Connect Four Game",
        version=version("connect_four"),
        version_flags=["--version", "-v"],
        help_format="rich",
    )

    app.command(create_nats_streams)

    app.command(create_game)
    app.command(end_game)

    app.command(run_message_consumer)
    app.command(run_task_scheduler)
    app.command(run_task_executor)

    return app


async def create_nats_streams(nats_url: str) -> None:
    """
    Create nats stream with all subjects used by application.
    """
    nats_config = NATSConfig(url=nats_url)
    async for nats_client in nats_client_factory(nats_config):
        jetstream = nats_jetstream_factory(nats_client)
        stream_creator = NATSStreamCreator(jetstream)
        await stream_creator.create()


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


async def run_task_scheduler() -> None:
    """Run task scheduler."""
    task_scheduler = create_task_scheduler_app()
    await task_scheduler.startup()
    await run_scheduler_loop(task_scheduler)
    await task_scheduler.shutdown()


def run_task_executor(
    workers: Annotated[
        int,
        Parameter("--workers", show_default=True),
    ] = 2,
) -> None:
    """Run task executor."""
    worker_args = WorkerArgs(
        broker="connect_four.main.task_executor:task_executor",
        modules=["connect_four.presentation.task_executor"],
        tasks_pattern=("executors.py",),
        workers=workers,
        configure_logging=False,
    )
    run_worker(worker_args)
