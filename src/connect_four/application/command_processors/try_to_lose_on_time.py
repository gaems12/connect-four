# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from dataclasses import dataclass

from connect_four.domain import GameId, GameStateId, TryToLoseOnTime
from connect_four.application.common import (
    GameGateway,
    GameEndReason,
    GameEndedEvent,
    EventPublisher,
    CentrifugoClient,
    centrifugo_game_channel_factory,
    TransactionManager,
    GameDoesNotExistError,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class TryToLoseOnTimeCommand:
    game_id: GameId
    game_state_id: GameStateId


class TryToLoseOnTimeProcessor:
    __slots__ = (
        "_try_to_lose_on_time",
        "_game_gateway",
        "_event_publisher",
        "_centrifugo_client",
        "_transaction_manager",
    )

    def __init__(
        self,
        try_to_lose_on_time: TryToLoseOnTime,
        game_gateway: GameGateway,
        event_publisher: EventPublisher,
        centrifugo_client: CentrifugoClient,
        transaction_manager: TransactionManager,
    ):
        self._try_to_lose_on_time = try_to_lose_on_time
        self._game_gateway = game_gateway
        self._event_publisher = event_publisher
        self._centrifugo_client = centrifugo_client
        self._transaction_manager = transaction_manager

    async def process(self, command: TryToLoseOnTimeCommand) -> None:
        game = await self._game_gateway.by_id(
            id=command.game_id,
            acquire=True,
        )
        if not game:
            raise GameDoesNotExistError()

        game_is_ended = self._try_to_lose_on_time(
            game=game,
            game_state_id=command.game_state_id,
        )
        if not game_is_ended:
            return

        await self._game_gateway.update(game)

        event = GameEndedEvent(
            game_id=game.id,
            move=None,
            players=game.players,
            reason=GameEndReason.TIME_IS_UP,
            last_turn=game.current_turn,
        )
        await self._event_publisher.publish(event)

        players = {
            player_id.hex: {
                "chip_type": player_state.chip_type.value,
                "time_left": player_state.time_left.total_seconds(),
            }
            for player_id, player_state in game.players.items()
        }
        centrifugo_publication = {
            "type": "game_ended",
            "move": None,
            "players": players,
            "reason": GameEndReason.TIME_IS_UP,
            "last_turn": game.current_turn.hex,
        }
        await self._centrifugo_client.publish(
            channel=centrifugo_game_channel_factory(game.id),
            data=centrifugo_publication,  # type: ignore[arg-type]
        )

        await self._transaction_manager.commit()
