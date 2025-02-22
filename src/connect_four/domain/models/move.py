# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class Move:
    column: int
    row: int
