# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from urllib.parse import urljoin
from dataclasses import dataclass

from httpx import AsyncClient

from connect_four.domain import GameId
from connect_four.application import (
    LobbyId,
    GameCreatedEvent,
    GameStartedEvent,
    GameEndedEvent,
    MoveAcceptedEvent,
    MoveRejectedEvent,
    Event,
)
from connect_four.infrastructure.utils import get_env_var


type _Serializable = (
    str
    | int
    | float
    | bytes
    | None
    | list[_Serializable]
    | dict[str, _Serializable]
)


def load_centrifugo_config() -> "CentrifugoConfig":
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

        elif isinstance(event, GameStartedEvent):
            await self._publish_game_started(event)

        elif isinstance(event, GameEndedEvent):
            await self._publish_game_ended(event)

        elif isinstance(event, MoveAcceptedEvent):
            await self._publish_move_accepted(event)

        elif isinstance(event, MoveRejectedEvent):
            await self._publish_move_rejected(event)

    async def _publish_game_created(
        self,
        event: GameCreatedEvent,
    ) -> None:
        players = {
            player_id.hex: {
                "chip_type": player_state.chip_type.value,
                "time_left": player_state.time_left.total_seconds(),
            }
            for player_id, player_state in event.players.items()
        }
        event_as_dict = {
            "type": "game_created",
            "game_id": event.game_id.hex,
            "players": players,
            "current_turn": event.current_turn.hex,
        }
        await self._publish(
            channel=self._lobby_channel_factory(event.lobby_id),
            data=event_as_dict,  # type: ignore
        )

    async def _publish_game_started(
        self,
        event: GameStartedEvent,
    ) -> None:
        await self._publish(
            channel=self._game_channel_factory(event.game_id),
            data={"type": "game_started"},
        )

    async def _publish_game_ended(
        self,
        event: GameEndedEvent,
    ) -> None:
        if event.move:
            move = {
                "row": event.move.row,
                "column": event.move.column,
            }
        else:
            move = None

        players = {
            player_id.hex: {
                "chip_type": player_state.chip_type.value,
                "time_left": player_state.time_left.total_seconds(),
            }
            for player_id, player_state in event.players.items()
        }
        event_as_dict = {
            "type": "game_ended",
            "move": move,
            "players": players,
            "reason": event.reason,
            "last_turn": event.last_turn.hex,
        }
        await self._publish(
            channel=self._game_channel_factory(event.game_id),
            data=event_as_dict,  # type: ignore
        )

    async def _publish_move_accepted(
        self,
        event: MoveAcceptedEvent,
    ) -> None:
        move = {
            "row": event.move.row,
            "column": event.move.column,
        }
        players = {
            player_id.hex: {
                "chip_type": player_state.chip_type.value,
                "time_left": player_state.time_left.total_seconds(),
            }
            for player_id, player_state in event.players.items()
        }
        event_as_dict = {
            "type": "move_accepted",
            "move": move,
            "players": players,
            "current_turn": event.current_turn.hex,
        }
        await self._publish(
            channel=self._game_channel_factory(event.game_id),
            data=event_as_dict,  # type: ignore
        )

    async def _publish_move_rejected(
        self,
        event: MoveRejectedEvent,
    ) -> None:
        move = {
            "row": event.move.row,
            "column": event.move.column,
        }
        players = {
            player_id.hex: {
                "chip_type": player_state.chip_type.value,
                "time_left": player_state.time_left.total_seconds(),
            }
            for player_id, player_state in event.players.items()
        }
        event_as_dict = {
            "type": "move_rejected",
            "move": move,
            "players": players,
            "reason": event.reason,
            "current_turn": event.current_turn.hex,
        }
        await self._publish(
            channel=self._game_channel_factory(event.game_id),
            data=event_as_dict,  # type: ignore
        )

    def _game_channel_factory(self, game_id: GameId) -> str:
        return f"game:{game_id.hex}"

    def _lobby_channel_factory(self, lobby_id: LobbyId) -> str:
        return f"lobby:{lobby_id.hex}"

    async def _publish(
        self,
        *,
        channel: str,
        data: _Serializable,
    ) -> None:
        await self._send_request(
            method="publish",
            payload={"channel": channel, "data": data},
        )

    async def _send_request(
        self,
        *,
        method: str,
        payload: _Serializable,
    ) -> None:
        response = await self._httpx_client.post(
            url=urljoin(self._config.url, method),
            json=payload,
            headers={"X-API-Key": self._config.api_key},
        )
        response.raise_for_status()
