# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from dataclasses import dataclass

from connect_four.domain.constants import MoveRejectionReason
from .chip_location import ChipLocation


@dataclass(frozen=True, slots=True)
class MoveAccepted:
    chip_location: ChipLocation


@dataclass(frozen=True, slots=True)
class MoveRejected:
    reason: MoveRejectionReason


@dataclass(frozen=True, slots=True)
class Win:
    chip_location: ChipLocation


@dataclass(frozen=True, slots=True)
class LossByTime:
    chip_location: ChipLocation


@dataclass(frozen=True, slots=True)
class Draw:
    chip_location: ChipLocation


type MoveResult = MoveAccepted | MoveRejected | Win | LossByTime | Draw
