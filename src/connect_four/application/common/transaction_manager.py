# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from typing import Protocol


class TransactionManager(Protocol):
    async def commit(self) -> None:
        raise NotImplementedError
