# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from dataclasses import dataclass
from datetime import datetime, timedelta

from four_in_a_row.domain import UserId, GameId, CreateGame
from four_in_a_row.application.common import (
    SortGamesBy,
    GameGateway,
    GameCreatedEvent,
    EventPublisher,
    TransactionManager,
    GameAlreadyExistsError,
)


@dataclass(frozen=True, slots=True)
class CreateGameCommand:
    game_id: GameId
    first_player_id: UserId
    second_player_id: UserId
    time_for_each_player: timedelta
    created_at: datetime


class CreateGameProcessor:
    __slots__ = (
        "_create_game",
        "_game_gateway",
        "_event_publisher",
        "_transaction_manager",
    )

    def __init__(
        self,
        create_game: CreateGame,
        game_gateway: GameGateway,
        event_publisher: EventPublisher,
        transaction_manager: TransactionManager,
    ):
        self._create_game = create_game
        self._game_gateway = game_gateway
        self._event_publisher = event_publisher
        self._transaction_manager = transaction_manager

    async def process(self, command: CreateGameCommand) -> None:
        game = await self._game_gateway.by_id(command.game_id)
        if game:
            raise GameAlreadyExistsError()

        games = await self._game_gateway.list_by_player_ids(
            player_ids=(command.first_player_id, command.second_player_id),
            sort_by=SortGamesBy.DESC_CREATED_AT,
            limit=1,
        )
        if games:
            last_game = games[0]
        else:
            last_game = None

        new_game = self._create_game(
            id=command.game_id,
            first_player_id=command.first_player_id,
            second_player_id=command.second_player_id,
            created_at=command.created_at,
            time_for_each_player=command.time_for_each_player,
            last_game=last_game,
        )
        await self._game_gateway.save(new_game)

        event = GameCreatedEvent(
            game_id=new_game.id,
            board=new_game.board,
            players=new_game.players,
            current_turn=new_game.current_turn,
        )
        await self._event_publisher.publish(event)

        await self._transaction_manager.commit()
