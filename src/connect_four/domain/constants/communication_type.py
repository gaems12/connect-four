# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = ("CommunicatonType",)

from enum import StrEnum


class CommunicatonType(StrEnum):
    CENTRIFUGO = "centrifugo"
    OTHER = "other"
