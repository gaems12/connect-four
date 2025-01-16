# Copyright (c) 2024, Egor Romanov.
# All rights reserved.


class ApplicationError(Exception): ...


class GameDoesNotExistError(ApplicationError): ...
