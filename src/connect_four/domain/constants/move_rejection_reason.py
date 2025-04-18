# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from enum import StrEnum


class MoveRejectionReason(StrEnum):
    GAME_IS_ENDED = "game_is_ended"
    OTHER_PLAYER_TURN = "other_player_turn"
    ILLEGAL_MOVE = "illegal_move"
