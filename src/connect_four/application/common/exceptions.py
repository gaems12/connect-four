# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).


class ApplicationError(Exception): ...


class GameAlreadyExistsError(ApplicationError): ...


class GameDoesNotExistError(ApplicationError): ...
