# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from enum import StrEnum


class GameStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    ENDED = "ended"
