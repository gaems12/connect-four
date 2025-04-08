# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from unittest.mock import AsyncMock
from datetime import datetime, timedelta, timezone
from typing import Final

from uuid_extensions import uuid7

from connect_four.domain import (
    ChipType,
    BOARD_COLUMNS,
    BOARD_ROWS,
    GameId,
    UserId,
    LobbyId,
    PlayerState,
    CreateGame,
)
from connect_four.application import (
    GameCreatedEvent,
    CreateGameCommand,
    CreateGameProcessor,
)
from .fakes import (
    FakeGameGateway,
    FakeEventPublisher,
    FakeCentrifugoClient,
)


_GAME_ID: Final = GameId(uuid7())
_LOBBY_ID: Final = LobbyId(uuid7())

_FIRST_PLAYER_ID: Final = UserId(uuid7())
_SECOND_PLAYER_ID: Final = UserId(uuid7())

_TIME_FOR_EACH_PLAYER: Final = timedelta(minutes=1)


async def test_create_game_processor():
    event_publisher = FakeEventPublisher()
    centrifugo_client = FakeCentrifugoClient()

    command = CreateGameCommand(
        game_id=_GAME_ID,
        lobby_id=_LOBBY_ID,
        first_player_id=_FIRST_PLAYER_ID,
        second_player_id=_SECOND_PLAYER_ID,
        time_for_each_player=_TIME_FOR_EACH_PLAYER,
        created_at=datetime.now(timezone.utc),
    )
    command_processor = CreateGameProcessor(
        create_game=CreateGame(),
        game_gateway=FakeGameGateway(),
        event_publisher=event_publisher,
        centrifugo_client=centrifugo_client,
        transaction_manager=AsyncMock(),
    )

    await command_processor.process(command)

    players = {
        _FIRST_PLAYER_ID: PlayerState(
            chip_type=ChipType.FIRST,
            time_left=_TIME_FOR_EACH_PLAYER,
        ),
        _SECOND_PLAYER_ID: PlayerState(
            chip_type=ChipType.SECOND,
            time_left=_TIME_FOR_EACH_PLAYER,
        ),
    }
    expected_event = GameCreatedEvent(
        game_id=_GAME_ID,
        lobby_id=_LOBBY_ID,
        board=[[None] * BOARD_COLUMNS for _ in range(BOARD_ROWS)],
        players=players,
        current_turn=_FIRST_PLAYER_ID,
    )
    assert expected_event in event_publisher.events

    centrifugo_publication_players = {
        _FIRST_PLAYER_ID.hex: {
            "chip_type": ChipType.FIRST,
            "time_left": _TIME_FOR_EACH_PLAYER.total_seconds(),
        },
        _SECOND_PLAYER_ID.hex: {
            "chip_type": ChipType.SECOND,
            "time_left": _TIME_FOR_EACH_PLAYER.total_seconds(),
        },
    }
    expected_centrifugo_publication = {
        "type": "game_created",
        "game_id": _GAME_ID.hex,
        "players": centrifugo_publication_players,
        "current_turn": _FIRST_PLAYER_ID.hex,
    }
    assert (
        centrifugo_client.publications[f"lobbies:{_LOBBY_ID.hex}"]
        == expected_centrifugo_publication
    )
