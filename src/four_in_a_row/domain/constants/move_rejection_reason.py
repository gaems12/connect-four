# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from enum import StrEnum


class MoveRejectionReason(StrEnum):
    GAME_IS_FINISHED = "game_is_finished"
    OTHER_PLAYER_TURN = "other_player_turn"
    ILLEGAL_MOVE = "illegal_move"
