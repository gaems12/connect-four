# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from dataclasses import dataclass
from datetime import timedelta

from redis.asyncio.client import Redis

from four_in_a_row.infrastructure.utils import (
    get_env_var,
    str_to_timedelta,
)


def lock_manager_config_from_env() -> "LockManagerConfig":
    return LockManagerConfig(
        lock_expires_in=get_env_var(
            key="LOCK_EXPIRES_IN",
            value_factory=str_to_timedelta,
        ),
    )


@dataclass(frozen=True, slots=True)
class LockManagerConfig:
    lock_expires_in: timedelta


class LockManager:
    __slots__ = (
        "_redis",
        "_acquired_lock_names",
        "_config",
    )

    def __init__(self, redis: Redis, config: LockManagerConfig):
        self._redis = redis
        self._acquired_lock_names: list[str] = []
        self._config = config

    async def acquire(self, lock_id: str) -> None:
        lock_name = self._lock_name_factory(lock_id)
        if lock_name in self._acquired_lock_names:
            return

        lock_is_acquired = await self._redis.get(lock_name)
        while lock_is_acquired:
            lock_is_acquired = await self._redis.get(lock_name)

        await self._redis.set(
            name=lock_name,
            value="",
            ex=self._config.lock_expires_in,
        )
        self._acquired_lock_names.append(lock_name)

    async def release_all(self) -> None:
        await self._redis.delete(*self._acquired_lock_names)
        self._acquired_lock_names.clear()

    def _lock_name_factory(self, lock_id: str) -> str:
        return f"locks:{lock_id}"
