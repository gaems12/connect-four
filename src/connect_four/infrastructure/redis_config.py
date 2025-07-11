# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = ("RedisConfig", "load_redis_config")

from dataclasses import dataclass

from .utils import get_env_var


def load_redis_config() -> "RedisConfig":
    return RedisConfig(
        url=get_env_var("REDIS_URL", default="redis://localhost:6379"),
    )


@dataclass(frozen=True, slots=True)
class RedisConfig:
    url: str
