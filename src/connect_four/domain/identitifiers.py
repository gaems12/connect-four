# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = ("GameId", "GameStateId", "UserId")

from typing import NewType
from uuid import UUID


GameId = NewType("GameId", UUID)
GameStateId = NewType("GameStateId", UUID)
UserId = NewType("UserId", UUID)
