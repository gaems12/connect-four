# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = (
    "NATSConfig",
    "load_nats_config",
)

from dataclasses import dataclass

from connect_four.infrastructure.utils import get_env_var


def load_nats_config() -> "NATSConfig":
    return NATSConfig(
        url=get_env_var("NATS_URL", default="nats://localhost:4222"),
    )


@dataclass(frozen=True, slots=True)
class NATSConfig:
    url: str
