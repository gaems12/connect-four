# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from typing import Protocol

from connect_four.domain import GameId, LobbyId


type Serializable = (
    str
    | int
    | float
    | bytes
    | None
    | list[Serializable]
    | dict[str, Serializable]
)


def centrifugo_lobby_channel_factory(lobby_id: LobbyId) -> str:
    return f"lobby:{lobby_id.hex}"


def centrifugo_game_channel_factory(game_id: GameId) -> str:
    return f"game:{game_id.hex}"


class CentrifugoClient(Protocol):
    async def publish(
        self,
        *,
        channel: str,
        data: Serializable,
    ) -> None:
        raise NotImplementedError
