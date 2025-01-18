# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

__all__ = ("HTTPIdentityProvider",)

from uuid import UUID

from fastapi import Request

from four_in_a_row.domain import UserId
from four_in_a_row.application import IdentityProvider


class HTTPIdentityProvider(IdentityProvider):
    __slots__ = ("_request",)

    def __init__(self, request: Request):
        self._request = request

    async def user_id(self) -> UserId:
        request_json = await self._request.json()
        if not request_json or not isinstance(request_json, dict):
            raise Exception("HTTP request's JSON cannot be converter to dict.")

        user_id = request_json.get("user")
        return UserId(UUID(user_id))
