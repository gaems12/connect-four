# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from urllib.parse import urljoin
from dataclasses import dataclass

from httpx import AsyncClient

from four_in_a_row.domain import GameId
from four_in_a_row.application import GameCreatedEvent, Event
from four_in_a_row.infrastructure.utils import get_env_var


type _Serializable = (
    str
    | int
    | float
    | bytes
    | None
    | list[_Serializable]
    | dict[str, _Serializable]
)


def centrifugo_config_from_env() -> "CentrifugoConfig":
    return CentrifugoConfig(
        url=get_env_var("CENTRIFUGO_URL"),
        api_key=get_env_var("CENTRIFUGO_API_KEY"),
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class CentrifugoConfig:
    url: str
    api_key: str


class HTTPXCentrifugoClient:
    __slots__ = ("_httpx_client", "_config")

    def __init__(
        self,
        httpx_client: AsyncClient,
        config: CentrifugoConfig,
    ):
        self._httpx_client = httpx_client
        self._config = config

    async def publish_event(self, event: Event) -> None:
        if isinstance(event, GameCreatedEvent):
            await self._publish_game_created(event)

    async def _publish_game_created(
        self,
        event: GameCreatedEvent,
    ) -> None:
        event_as_dict: dict[str, _Serializable] = {
            "players": list(map(lambda user_id: user_id.hex, event.players)),
            "current_turn": event.current_turn.hex,
        }
        await self._publish(
            channel=self._game_channel_factory(event.id),
            data=event_as_dict,
        )

    def _game_channel_factory(self, game_id: GameId) -> str:
        return f"game:{game_id}"

    async def _publish(
        self,
        *,
        channel: str,
        data: dict[str, _Serializable],
    ) -> None:
        await self._send_request(
            method="publish",
            payload={"channel": channel, "data": data},
        )

    async def _send_request(
        self,
        *,
        method: str,
        payload: dict[str, _Serializable],
    ) -> None:
        response = await self._httpx_client.post(
            url=urljoin(self._config.url, method),
            json=payload,
            headers={"Authorization": f"apikey {self._config.api_key}"},
        )
        response.raise_for_status()
