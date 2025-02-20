# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from dataclasses import dataclass

from g_logger import GLoggerLevel

from connect_four.infrastructure.utils import get_env_var


def load_logging_config() -> "LoggingConfig":
    return LoggingConfig(
        level=get_env_var("LOGGING_LEVEL", GLoggerLevel),
    )


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    level: GLoggerLevel
