# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

import asyncio
import random
import traceback
from urllib.parse import urljoin
from dataclasses import dataclass
from typing import Final

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
from connect_four.infrastructure.log import RequestLogger
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

_MAX_RETRIES: Final = 20
_BASE_BACKOFF_DELAY: Final = 0.5
_MAX_BACKOFF_DELAY: Final = 10


class CentrifuoClientError(Exception): ...


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
    __slots__ = ("_httpx_client", "_config", "_logger")

    def __init__(
        self,
        httpx_client: AsyncClient,
        config: CentrifugoConfig,
        logger: RequestLogger,
    ):
        self._httpx_client = httpx_client
        self._config = config
        self._logger = logger

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
            url=urljoin(self._config.url, "publish"),
            json_={"channel": channel, "data": data},
            retry_on_failure=True,
        )

    async def _send_request(
        self,
        *,
        url: str,
        json_: _Serializable,
        retry_on_failure: bool,
    ) -> None:
        try:
            self._logger.debug(
                message="Going to make request to centrifugo.",
                url=url,
                json=json_,
            )
            response = await self._httpx_client.post(
                url=url,
                json=json_,
                headers={"X-API-Key": self._config.api_key},
            )
        except Exception as e:
            error_message = (
                "Unexpected error occurred during request to centrifugo."
            )
            self._logger.error(
                message=error_message,
                traceback=traceback.format_exception(e),
            )

            if retry_on_failure:
                retries_were_successful = await self._retry_request(
                    url=url,
                    json_=json_,
                )
                if retries_were_successful:
                    return

            raise CentrifuoClientError(error_message)

        if response.status_code == 200:
            self._logger.debug(
                message="Centrifuo responded.",
                status_code=response.status_code,
                content=response.content.decode(),
            )
            return

        error_message = "Centrifugo responded with bad status code."
        self._logger.error(
            message=error_message,
            status_code=response.status_code,
            content=response.content.decode(),
        )

        if retry_on_failure:
            retries_were_successful = await self._retry_request(
                url=url,
                json_=json_,
            )
            if retries_were_successful:
                return

        raise CentrifuoClientError(error_message)

    async def _retry_request(
        self,
        *,
        url: str,
        json_: _Serializable,
    ) -> bool:
        for retry_number in range(1, _MAX_RETRIES + 1):
            try:
                self._logger.debug(
                    message="Going to retry request to centrifugo.",
                    retry_number=retry_number,
                    retries_left=_MAX_RETRIES - retry_number,
                )
                await self._send_request(
                    url=url,
                    json_=json_,
                    retry_on_failure=False,
                )
                return True

            except CentrifuoClientError:
                if retry_number == _MAX_RETRIES:
                    return False

                wait_time = self._calculate_backoff_wait_time(retry_number)
                await asyncio.sleep(wait_time)

        return False

    def _calculate_backoff_wait_time(self, retry_number: int) -> float:
        return min(
            _BASE_BACKOFF_DELAY * (2**retry_number) + random.uniform(0, 0.5),
            _MAX_BACKOFF_DELAY,
        )
