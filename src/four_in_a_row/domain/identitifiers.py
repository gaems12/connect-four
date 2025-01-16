# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

__all__ = ("GameId", "GameStateId", "UserId")

from typing import NewType
from uuid import UUID


GameId = NewType("GameId", UUID)
GameStateId = NewType("GameStateId", UUID)
UserId = NewType("UserId", UUID)
