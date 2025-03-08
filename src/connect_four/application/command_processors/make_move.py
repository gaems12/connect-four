# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Final

from connect_four.domain import (
    GameId,
    Game,
    MoveAccepted,
    MoveRejected,
    Win,
    Draw,
    LossByTime,
    MoveResult,
    MakeMove,
)
from connect_four.application import (
    GameGateway,
    GameEndReason,
    MoveAcceptedEvent,
    MoveRejectedEvent,
    GameEndedEvent,
    Event,
    EventPublisher,
    TryToLoseByTimeTask,
    TaskScheduler,
    CentrifugoClient,
    centrifugo_game_channel_factory,
    TransactionManager,
    IdentityProvider,
    GameDoesNotExistError,
)


_MOVE_RESULT_TO_GAME_END_REASON_MAP: Final = {
    Win: GameEndReason.WIN,
    Draw: GameEndReason.DRAW,
    LossByTime: GameEndReason.LOSS_BY_TIME,
}


@dataclass(frozen=True, slots=True, kw_only=True)
class MakeMoveCommand:
    game_id: GameId
    column: int


class MakeMoveProcessor:
    __slots__ = (
        "_make_move",
        "_game_gateway",
        "_event_publisher",
        "_task_scheduler",
        "_centrifugo_client",
        "_transaction_manager",
        "_identity_provider",
    )

    def __init__(
        self,
        make_move: MakeMove,
        game_gateway: GameGateway,
        event_publisher: EventPublisher,
        task_scheduler: TaskScheduler,
        centrifugo_client: CentrifugoClient,
        transaction_manager: TransactionManager,
        identity_provider: IdentityProvider,
    ):
        self._make_move = make_move
        self._game_gateway = game_gateway
        self._event_publisher = event_publisher
        self._task_scheduler = task_scheduler
        self._centrifugo_client = centrifugo_client
        self._transaction_manager = transaction_manager
        self._identity_provider = identity_provider

    async def process(self, command: MakeMoveCommand) -> None:
        current_user_id = await self._identity_provider.user_id()

        game = await self._game_gateway.by_id(
            id=command.game_id,
            acquire=True,
        )
        if not game:
            raise GameDoesNotExistError()

        old_game_state_id = game.state_id

        move_result = self._make_move(
            game=game,
            current_player_id=current_user_id,
            column=command.column,
        )
        await self._game_gateway.update(game)

        if not isinstance(move_result, MoveRejected):
            await self._task_scheduler.unschedule(old_game_state_id)

        if isinstance(move_result, MoveAccepted):
            current_player_state = game.players[current_user_id]
            time_left_for_current_player = current_player_state.time_left

            execute_task_at = (
                datetime.now(timezone.utc) + time_left_for_current_player
            )
            task = TryToLoseByTimeTask(
                id=game.state_id,
                execute_at=execute_task_at,
                game_id=game.id,
                game_state_id=game.state_id,
            )
            await self._task_scheduler.schedule(task)

        await self._publish_event(
            game=game,
            move_result=move_result,
        )
        await self._publish_data_to_centrifugo(
            game=game,
            move_result=move_result,
        )

        await self._transaction_manager.commit()

    async def _publish_event(
        self,
        *,
        game: Game,
        move_result: MoveResult,
    ) -> None:
        event: Event

        if isinstance(move_result, MoveAccepted):
            event = MoveAcceptedEvent(
                game_id=game.id,
                chip_location=move_result.chip_location,
                players=game.players,
                current_turn=game.current_turn,
            )

        elif isinstance(move_result, MoveRejected):
            event = MoveRejectedEvent(
                game_id=game.id,
                reason=move_result.reason,
                players=game.players,
                current_turn=game.current_turn,
            )

        elif isinstance(move_result, (Win, Draw, LossByTime)):
            reason = _MOVE_RESULT_TO_GAME_END_REASON_MAP[type(move_result)]
            event = GameEndedEvent(
                game_id=game.id,
                chip_location=move_result.chip_location,
                players=game.players,
                reason=reason,
                last_turn=game.current_turn,
            )

        await self._event_publisher.publish(event)

    async def _publish_data_to_centrifugo(
        self,
        *,
        game: Game,
        move_result: MoveResult,
    ) -> None:
        if isinstance(move_result, MoveAccepted):
            raw_chip_location = {
                "row": move_result.chip_location.row,
                "column": move_result.chip_location.column,
            }
            raw_players = {
                player_id.hex: {
                    "chip_type": player_state.chip_type.value,
                    "time_left": player_state.time_left.total_seconds(),
                }
                for player_id, player_state in game.players.items()
            }
            centrifugo_publication = {
                "type": "move_accepted",
                "chip_location": raw_chip_location,  # type: ignore[dict-item]
                "players": raw_players,  # type: ignore[dict-item]
                "current_turn": game.current_turn.hex,
            }

        elif isinstance(move_result, MoveRejected):
            raw_players = {
                player_id.hex: {
                    "chip_type": player_state.chip_type.value,
                    "time_left": player_state.time_left.total_seconds(),
                }
                for player_id, player_state in game.players.items()
            }
            centrifugo_publication = {
                "type": "move_rejected",
                "players": raw_players,  # type: ignore[dict-item]
                "reason": move_result.reason,
                "current_turn": game.current_turn.hex,
            }

        elif isinstance(move_result, (Win, Draw, LossByTime)):
            reason = _MOVE_RESULT_TO_GAME_END_REASON_MAP[type(move_result)]

            raw_chip_location = {
                "row": move_result.chip_location.row,
                "column": move_result.chip_location.column,
            }
            raw_players = {
                player_id.hex: {
                    "chip_type": player_state.chip_type.value,
                    "time_left": player_state.time_left.total_seconds(),
                }
                for player_id, player_state in game.players.items()
            }
            centrifugo_publication = {
                "type": "game_ended",
                "chip_location": raw_chip_location,  # type: ignore[dict-item]
                "players": raw_players,  # type: ignore[dict-item]
                "reason": reason,
                "last_turn": game.current_turn.hex,
            }

        await self._centrifugo_client.publish(
            channel=centrifugo_game_channel_factory(game.id),
            data=centrifugo_publication,  # type: ignore[arg-type]
        )
