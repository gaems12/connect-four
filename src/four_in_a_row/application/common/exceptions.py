# Copyright (c) 2024, Egor Romanov.
# All rights reserved.


class ApplicationError(Exception): ...


class GameAlreadyExistsError(ApplicationError): ...


class GameDoesNotExistError(ApplicationError): ...
