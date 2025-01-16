# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from typing import Protocol

from four_in_a_row.domain import UserId


class IdentityProvider(Protocol):
    async def user_id(self) -> UserId:
        raise NotImplementedError
