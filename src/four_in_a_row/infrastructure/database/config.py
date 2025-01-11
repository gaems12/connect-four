# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from dataclasses import dataclass

from four_in_a_row.infrastructure.utils import get_env_var


def redis_config_from_env() -> "RedisConfig":
    return RedisConfig(url=get_env_var("REDIS_URL"))


@dataclass(frozen=True, slots=True)
class RedisConfig:
    url: str
