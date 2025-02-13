# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from dataclasses import dataclass

from connect_four.domain import GameId, GameStateId, TryToLoseOnTime
from connect_four.application.common import (
    GameGateway,
    GameEndReason,
    GameEndedEvent,
    EventPublisher,
    TransactionManager,
    GameDoesNotExistError,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class LoseOnTimeCommand:
    game_id: GameId
    game_state_id: GameStateId


class LoseOnTimeProcessor:
    __slots__ = (
        "_try_to_lose_on_time",
        "_game_gateway",
        "_event_publisher",
        "_transaction_manager",
    )

    def __init__(
        self,
        try_to_lose_on_time: TryToLoseOnTime,
        game_gateway: GameGateway,
        event_publisher: EventPublisher,
        transaction_manager: TransactionManager,
    ):
        self._try_to_lose_on_time = try_to_lose_on_time
        self._game_gateway = game_gateway
        self._event_publisher = event_publisher
        self._transaction_manager = transaction_manager

    async def process(self, command: LoseOnTimeCommand) -> None:
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

        await self._transaction_manager.commit()
