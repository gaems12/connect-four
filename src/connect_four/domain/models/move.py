# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class Move:
    column: int
    row: int
