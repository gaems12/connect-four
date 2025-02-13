# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from dataclasses import dataclass

from connect_four.infrastructure.utils import get_env_var


def load_nats_config() -> "NATSConfig":
    return NATSConfig(url=get_env_var("NATS_URL"))


@dataclass(frozen=True, slots=True)
class NATSConfig:
    url: str
