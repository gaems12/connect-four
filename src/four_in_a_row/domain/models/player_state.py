# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from dataclasses import dataclass
from datetime import timedelta

from four_in_a_row.domain.constants import ChipType


@dataclass(slots=True, kw_only=True)
class PlayerState:
    chip_type: ChipType
    time_left: timedelta
