# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = ("CreateGameCommand", "CreateGameProcessor")

from dataclasses import dataclass
from datetime import datetime

from connect_four.domain import (
    CommunicatonType,
    GameId,
    LobbyId,
    Game,
    Player,
    CreateGame,
)
from connect_four.application.common import (
    SortGamesBy,
    GameGateway,
    GameCreatedEvent,
    EventPublisher,
    Serializable,
    CentrifugoClient,
    centrifugo_lobby_channel_factory,
    TransactionManager,
    GameAlreadyExistsError,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateGameCommand:
    game_id: GameId
    lobby_id: LobbyId
    first_player: Player
    second_player: Player
    created_at: datetime


class CreateGameProcessor:
    __slots__ = (
        "_create_game",
        "_game_gateway",
        "_event_publisher",
        "_centrifugo_client",
        "_transaction_manager",
    )

    def __init__(
        self,
        create_game: CreateGame,
        game_gateway: GameGateway,
        event_publisher: EventPublisher,
        centrifugo_client: CentrifugoClient,
        transaction_manager: TransactionManager,
    ):
        self._create_game = create_game
        self._game_gateway = game_gateway
        self._event_publisher = event_publisher
        self._centrifugo_client = centrifugo_client
        self._transaction_manager = transaction_manager

    async def process(self, command: CreateGameCommand) -> None:
        game = await self._game_gateway.by_id(command.game_id)
        if game:
            raise GameAlreadyExistsError()

        games = await self._game_gateway.list_by_player_ids(
            player_ids=(command.first_player.id, command.second_player.id),
            sort_by=SortGamesBy.DESC_CREATED_AT,
            limit=1,
        )
        if games:
            last_game = games[0]
        else:
            last_game = None

        new_game = self._create_game(
            game_id=command.game_id,
            first_player=command.first_player,
            second_player=command.second_player,
            created_at=command.created_at,
            last_game=last_game,
        )
        await self._game_gateway.save(new_game)

        event = GameCreatedEvent(
            game_id=new_game.id,
            lobby_id=command.lobby_id,
            board=new_game.board,
            players=new_game.players,
            current_turn=new_game.current_turn,
        )
        await self._event_publisher.publish(event)

        player_communication_types = (
            command.first_player.communication_type,
            command.second_player.communication_type,
        )
        should_make_requests_to_centrifugo = any(
            (
                nt == CommunicatonType.CENTRIFUGO
                for nt in player_communication_types
            ),
        )
        if should_make_requests_to_centrifugo:
            await self._make_requests_to_centrifugo(
                lobby_id=command.lobby_id,
                new_game=new_game,
            )

        await self._transaction_manager.commit()

    async def _make_requests_to_centrifugo(
        self,
        *,
        lobby_id: LobbyId,
        new_game: Game,
    ) -> None:
        players: Serializable = {
            player_id.hex: {
                "chip_type": player_state.chip_type,
                "time_left": player_state.time_left.total_seconds(),
            }
            for player_id, player_state in new_game.players.items()
        }
        centrifugo_publication: Serializable = {
            "type": "game_created",
            "game_id": new_game.id.hex,
            "players": players,
            "current_turn": new_game.current_turn.hex,
        }
        await self._centrifugo_client.publish(
            channel=centrifugo_lobby_channel_factory(lobby_id),
            data=centrifugo_publication,
        )
