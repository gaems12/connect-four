# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = ("PlayerState",)

from dataclasses import dataclass
from datetime import timedelta

from connect_four.domain.constants import ChipType, CommunicatonType


@dataclass(slots=True, kw_only=True)
class PlayerState:
    chip_type: ChipType
    time_left: timedelta
    communication_type: CommunicatonType
