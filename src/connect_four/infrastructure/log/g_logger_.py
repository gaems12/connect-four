# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from typing import NewType

from g_logger import GLogger

from connect_four.infrastructure.operation_id import OperationId
from .config import LoggingConfig


AppLogger = NewType("AppLogger", GLogger)  # type: ignore
RequestLogger = NewType("RequestLogger", GLogger)  # type: ignore


def app_logger_factory(config: LoggingConfig) -> AppLogger:
    logger = GLogger.create(
        "connect_four",
        level=config.level,
        log_dump_errors=True,
    )
    return AppLogger(logger)


def request_logger_factory(
    app_logger: AppLogger,
    operation_id: OperationId,
) -> RequestLogger:
    logger = app_logger.create_child(
        "operation",
        data={"operation_id": operation_id},
    )
    return RequestLogger(logger)
