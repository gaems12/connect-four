# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from typing import Protocol


class TransactionManager(Protocol):
    async def commit(self) -> None:
        raise NotImplementedError
