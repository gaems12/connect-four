# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = ("TryToLoseByTimeCommand", "TryToLoseByTimeProcessor")

from dataclasses import dataclass

from connect_four.domain import (
    CommunicatonType,
    GameId,
    GameStateId,
    Game,
    TryToLoseByTime,
)
from connect_four.application.common import (
    GameGateway,
    GameEndReason,
    GameEndedEvent,
    EventPublisher,
    Serializable,
    CentrifugoClient,
    centrifugo_game_channel_factory,
    TransactionManager,
    GameDoesNotExistError,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class TryToLoseByTimeCommand:
    game_id: GameId
    game_state_id: GameStateId


class TryToLoseByTimeProcessor:
    __slots__ = (
        "_try_to_lose_by_time",
        "_game_gateway",
        "_event_publisher",
        "_centrifugo_client",
        "_transaction_manager",
    )

    def __init__(
        self,
        try_to_lose_by_time: TryToLoseByTime,
        game_gateway: GameGateway,
        event_publisher: EventPublisher,
        centrifugo_client: CentrifugoClient,
        transaction_manager: TransactionManager,
    ):
        self._try_to_lose_by_time = try_to_lose_by_time
        self._game_gateway = game_gateway
        self._event_publisher = event_publisher
        self._centrifugo_client = centrifugo_client
        self._transaction_manager = transaction_manager

    async def process(self, command: TryToLoseByTimeCommand) -> None:
        game = await self._game_gateway.by_id(
            game_id=command.game_id,
            acquire=True,
        )
        if not game:
            raise GameDoesNotExistError()

        game_is_ended = self._try_to_lose_by_time(
            game=game,
            game_state_id=command.game_state_id,
        )
        if not game_is_ended:
            return

        await self._game_gateway.update(game)

        event = GameEndedEvent(
            game_id=game.id,
            chip_location=None,
            players=game.players,
            reason=GameEndReason.LOSS_BY_TIME,
            last_turn=game.current_turn,
        )
        await self._event_publisher.publish(event)

        player_communication_types = (
            player_state.communication_type
            for player_state in game.players.values()
        )
        should_make_requests_to_centrifugo = any(
            ct == CommunicatonType.CENTRIFUGO
            for ct in player_communication_types
        )
        if should_make_requests_to_centrifugo:
            await self._make_requests_to_centrifugo(game)

        await self._transaction_manager.commit()

    async def _make_requests_to_centrifugo(self, game: Game) -> None:
        players: Serializable = {
            player_id.hex: {
                "chip_type": player_state.chip_type.value,
                "time_left": player_state.time_left.total_seconds(),
            }
            for player_id, player_state in game.players.items()
        }
        centrifugo_publication: Serializable = {
            "type": "game_ended",
            "chip_location": None,
            "players": players,
            "reason": GameEndReason.LOSS_BY_TIME,
            "last_turn": game.current_turn.hex,
        }
        await self._centrifugo_client.publish(
            channel=centrifugo_game_channel_factory(game.id),
            data=centrifugo_publication,
        )
