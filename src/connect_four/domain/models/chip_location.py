# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = ("ChipLocation",)

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class ChipLocation:
    column: int
    row: int
