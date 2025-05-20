# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = ("MakeMove",)

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
    ChipLocation,
    Win,
    LossByTime,
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
        column: int,
    ) -> MoveResult:
        move_rejection_reason = self._validate_move(
            game=game,
            column=column,
            current_player_id=current_player_id,
        )
        if move_rejection_reason:
            return MoveRejected(reason=move_rejection_reason)

        chip_location = self._calculate_chip_location(
            game=game,
            column=column,
        )
        if not chip_location:
            return MoveRejected(reason=MoveRejectionReason.ILLEGAL_MOVE)

        current_player_lost_by_time = self._apply_turn_time(
            game=game,
            current_player_id=current_player_id,
        )
        if current_player_lost_by_time:
            return LossByTime(chip_location=chip_location)

        move_result = self._place_chip(
            game=game,
            chip_location=chip_location,
            current_player_id=current_player_id,
        )
        return move_result

    def _validate_move(
        self,
        *,
        game: Game,
        column: int,
        current_player_id: UserId,
    ) -> MoveRejectionReason | None:
        if current_player_id not in game.players:
            raise Exception("There is no current player in the game")

        if game.status == GameStatus.ENDED:
            return MoveRejectionReason.GAME_IS_ENDED

        if game.current_turn != current_player_id:
            return MoveRejectionReason.OTHER_PLAYER_TURN

        if column > BOARD_COLUMNS - 1:
            return MoveRejectionReason.ILLEGAL_MOVE

        return None

    def _calculate_chip_location(
        self,
        *,
        game: Game,
        column: int,
    ) -> ChipLocation | None:
        for row in range(BOARD_ROWS - 1, -1, -1):
            if game.board[row][column] is None:
                return ChipLocation(column=column, row=row)

        return None

    def _apply_turn_time(
        self,
        *,
        game: Game,
        current_player_id: UserId,
    ) -> bool:
        """
        Updates the game's state based on the time taken by the
        current player to make their move and returns flag
        indicating whether the current player lost by time.
        """
        current_datetime = datetime.now(timezone.utc)

        if game.status == GameStatus.NOT_STARTED:
            game.last_move_made_at = current_datetime
            return False

        time_for_move = current_datetime - game.last_move_made_at  # type: ignore
        time_left_for_current_player = game.players[
            current_player_id
        ].time_left

        if time_for_move >= time_left_for_current_player:
            game.players[current_player_id].time_left = timedelta(seconds=0)
            game.last_move_made_at = current_datetime

            game.state_id = GameStateId(uuid4())
            game.status = GameStatus.ENDED

            return True

        game.players[current_player_id].time_left -= time_for_move
        game.last_move_made_at = current_datetime

        return False

    def _place_chip(
        self,
        *,
        game: Game,
        chip_location: ChipLocation,
        current_player_id: UserId,
    ) -> MoveAccepted | Win | Draw:
        game.state_id = GameStateId(uuid4())

        current_player = game.players[current_player_id]
        current_player_chip_type = current_player.chip_type

        game.board[chip_location.row][chip_location.column] = (
            current_player_chip_type
        )

        if game.status == GameStatus.NOT_STARTED:
            game.status = GameStatus.IN_PROGRESS

            self._next_turn(
                game=game,
                current_player_id=current_player_id,
            )
            return MoveAccepted(chip_location=chip_location)

        player_won = self._check_if_player_won(
            board=game.board,
            chip_location=chip_location,
            current_player_chip_type=current_player_chip_type,
        )
        if player_won:
            game.status = GameStatus.ENDED
            return Win(chip_location=chip_location)

        board_is_full = self._check_if_board_is_full(game.board)
        if board_is_full:
            game.status = GameStatus.ENDED
            return Draw(chip_location=chip_location)

        self._next_turn(
            game=game,
            current_player_id=current_player_id,
        )
        return MoveAccepted(chip_location=chip_location)

    def _check_if_player_won(
        self,
        *,
        board: list[list[ChipType | None]],
        chip_location: ChipLocation,
        current_player_chip_type: ChipType,
    ) -> bool:
        for row_delta, column_delta in _DIRECTIONS:
            forward_count = self._count_chips_in_direction(
                board=board,
                row=chip_location.row,
                column=chip_location.column,
                row_delta=row_delta,
                column_delta=column_delta,
                chip_type=current_player_chip_type,
            )
            if forward_count == 4:
                return True

            backward_count = self._count_chips_in_direction(
                board=board,
                row=chip_location.row,
                column=chip_location.column,
                row_delta=-row_delta,
                column_delta=-column_delta,
                chip_type=current_player_chip_type,
            )
            if backward_count == 4:
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
