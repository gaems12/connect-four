# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from typing import Final
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from connect_four.domain.identitifiers import UserId, GameStateId
from connect_four.domain.constants import (
    ChipType,
    GameStatus,
    MoveRejectionReason,
    BOARD_COLUMNS,
    BOARD_ROWS,
)
from connect_four.domain.models import (
    Game,
    Move,
    GameStarted,
    PlayerWon,
    MoveAccepted,
    Draw,
    MoveRejected,
    MoveResult,
)


_DIRECTIONS: Final = (
    (0, 1),  # horizontal
    (1, 0),  # vertical
    (1, 1),  # diagonal ↖↘
    (1, -1),  # diagonal ↗↙
)


class MakeMove:
    def __call__(
        self,
        *,
        game: Game,
        current_player_id: UserId,
        move: Move,
    ) -> MoveResult:
        move_rejection_reason = self._vallidate_move(
            game=game,
            move=move,
            current_player_id=current_player_id,
        )
        if move_rejection_reason:
            return MoveRejected(reason=move_rejection_reason)

        no_time_left_for_current_player = self._apply_turn_time(
            game=game,
            current_player_id=current_player_id,
        )
        if no_time_left_for_current_player:
            game.state_id = GameStateId(uuid4())
            game.status = GameStatus.ENDED
            return MoveRejected(reason=MoveRejectionReason.TIME_IS_UP)

        move_result = self._make_move(
            game=game,
            move=move,
            current_player_id=current_player_id,
        )
        return move_result

    def _apply_turn_time(
        self,
        *,
        game: Game,
        current_player_id: UserId,
    ) -> bool:
        """
        Updates the game's state based on the time taken by the
        current player to make their move and returns flag indicating
        whether the current player's time has expired.
        """
        current_datetime = datetime.now(timezone.utc)

        if game.status == GameStatus.NOT_STARTED:
            game.last_move_made_at = current_datetime
            return False

        time_for_move = current_datetime - game.last_move_made_at  # type: ignore

        if time_for_move >= game.players[current_player_id].time_left:
            game.players[current_player_id].time_left = timedelta(seconds=0)
            game.last_move_made_at = current_datetime
            return True

        game.players[current_player_id].time_left -= time_for_move
        game.last_move_made_at = current_datetime

        return False

    def _vallidate_move(
        self,
        *,
        game: Game,
        move: Move,
        current_player_id: UserId,
    ) -> MoveRejectionReason | None:
        if current_player_id not in game.players:
            raise Exception("There is no current player in the game")

        if game.status == GameStatus.ENDED:
            return MoveRejectionReason.GAME_IS_ENDED

        if game.current_turn != current_player_id:
            return MoveRejectionReason.OTHER_PLAYER_TURN

        if (
            move.column > BOARD_COLUMNS - 1
            or move.row > BOARD_ROWS - 1
            or game.board[move.row][move.column]
        ):
            return MoveRejectionReason.ILLEGAL_MOVE

        if (
            move.row != BOARD_ROWS - 1
            and game.board[move.row + 1][move.column] is None
        ):
            return MoveRejectionReason.ILLEGAL_MOVE

        return None

    def _make_move(
        self,
        *,
        game: Game,
        move: Move,
        current_player_id: UserId,
    ) -> GameStarted | PlayerWon | Draw | MoveAccepted:
        game.state_id = GameStateId(uuid4())

        current_player_chip_type = game.players[current_player_id].chip_type
        game.board[move.row][move.column] = current_player_chip_type

        if game.status == GameStatus.NOT_STARTED:
            game.status = GameStatus.IN_PROGRESS

            self._next_turn(
                game=game,
                current_player_id=current_player_id,
            )
            return GameStarted(next_turn=game.current_turn)

        player_won = self._check_if_player_won(
            game=game,
            move=move,
            current_player_chip_type=current_player_chip_type,
        )
        if player_won:
            game.status = GameStatus.ENDED
            return PlayerWon()

        board_is_full = self._check_if_board_is_full(game.board)
        if board_is_full:
            game.status = GameStatus.ENDED
            return Draw()

        self._next_turn(
            game=game,
            current_player_id=current_player_id,
        )
        return MoveAccepted(next_turn=game.current_turn)

    def _check_if_player_won(
        self,
        *,
        game: Game,
        move: Move,
        current_player_chip_type: ChipType,
    ) -> bool:
        for row_delta, column_delta in _DIRECTIONS:
            forward_count = self._count_chips_in_direction(
                board=game.board,
                row=move.row,
                column=move.column,
                row_delta=row_delta,
                column_delta=column_delta,
                chip_type=current_player_chip_type,
            )
            if forward_count >= 4:
                return True

            backward_count = self._count_chips_in_direction(
                board=game.board,
                row=move.row,
                column=move.column,
                row_delta=-row_delta,
                column_delta=-column_delta,
                chip_type=current_player_chip_type,
            )
            if backward_count >= 4:
                return True

            total_count = (
                forward_count
                + backward_count
                - 1  # We counted played chip twice
            )
            if total_count >= 4:
                return True

        return False

    def _count_chips_in_direction(
        self,
        *,
        board: list[list[ChipType | None]],
        row: int,
        column: int,
        row_delta: int,
        column_delta: int,
        chip_type: ChipType,
    ) -> int:
        count = 0
        current_row, current_column = row, column

        while (
            0 <= current_row <= BOARD_ROWS - 1
            and 0 <= current_column <= BOARD_COLUMNS - 1
            and board[current_row][current_column] == chip_type
        ):
            count += 1
            current_row += row_delta
            current_column += column_delta

        return count

    def _check_if_board_is_full(
        self,
        board: list[list[ChipType | None]],
    ) -> bool:
        return not any(cell is None for row in board for cell in row)

    def _next_turn(
        self,
        *,
        game: Game,
        current_player_id: UserId,
    ) -> None:
        for player_id in game.players:
            if player_id != current_player_id:
                game.current_turn = player_id
                return

        raise Exception(
            "There is no other player in the game to assign the next turn to.",
        )
