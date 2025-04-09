# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from typing import Any, cast, overload
from uuid import UUID

from connect_four.domain import GameId, GameStateId, UserId, Game
from connect_four.application import (
    SortGamesBy,
    GameGateway,
    Event,
    EventPublisher,
    Task,
    TaskScheduler,
    Serializable,
    CentrifugoClient,
)


class FakeGameGateway(GameGateway):
    __slots__ = ("_games",)

    def __init__(self, games: list[Game] | None = None):
        self._games = {game.id: game for game in games or []}

    @property
    def games(self) -> list[Game]:
        return list(self._games.values())

    async def by_id(
        self,
        id: GameId,
        *,
        acquire: bool = False,
    ) -> Game | None:
        return self._games.get(id)

    async def list_by_player_ids(
        self,
        player_ids: tuple[UserId, UserId],
        *,
        sort_by: SortGamesBy | None = None,
        limit: int = 0,
    ) -> list[Game]:
        games = [
            game
            for game in self._games.values()
            if player_ids[0] in game.players and player_ids[1] in game.players
        ]
        if sort_by == SortGamesBy.DESC_CREATED_AT:
            games.sort(key=lambda g: g.created_at, reverse=True)

        if limit > 0:
            games = games[:limit]
        else:
            raise Exception(
                "Cannot list by player ids: "
                "limit is not a positive number or zero.",
            )

        return games

    async def save(self, game: Game) -> None:
        self._games[game.id] = game

    async def update(self, game: Game) -> None:
        self._games[game.id] = game


class FakeEventPublisher(EventPublisher):
    __slots__ = ("_events",)

    def __init__(self, events: list[Event] | None = None):
        self._events = events or []

    @property
    def events(self) -> list[Event]:
        return self._events

    async def publish(self, event: Event) -> None:
        self._events.append(event)


class FakeTaskScheduler(TaskScheduler):
    __slots__ = ("_tasks",)

    def __init__(self, tasks: list[Task] | None = None):
        self._tasks = {task.id: task for task in tasks or []}

    @property
    def tasks(self) -> list[Task]:
        return list(self._tasks.values())

    async def schedule(self, task: Task) -> None:
        self._tasks[task.id] = task

    async def unschedule(self, task_id: str) -> None:
        self._tasks.pop(task_id, None)


class FakeCentrifugoClient(CentrifugoClient):
    __slots__ = ("_publications",)

    def __init__(self, publications: dict[str, Serializable] | None = None):
        self._publications = publications or {}

    @property
    def publications(self) -> dict[str, Serializable]:
        return self._publications

    async def publish(self, *, channel: str, data: Serializable) -> None:
        self._publications[channel] = data


class _Anything:
    __slots__ = ("_name", "_type")

    def __init__(self, name: str, type_: type):
        self._name = name
        self._type = type_

    @classmethod
    @overload
    def create[TH: Any](
        cls,
        *,
        name: str,
        type_: type[Any],
        type_hint: type[TH],
    ) -> TH: ...

    @classmethod
    @overload
    def create[T: Any](
        cls,
        *,
        name: str,
        type_: type[T],
    ) -> T: ...

    @classmethod
    def create[T: Any, TH: Any](
        cls,
        *,
        name: str,
        type_: type[T],
        type_hint: type[TH] | None = None,
    ) -> T | TH:
        anything = _Anything(name, type_)
        if type_hint:
            return cast(TH, anything)

        return cast(T, anything)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, self._type):
            return NotImplemented
        return True

    def __ne__(self, value: object) -> bool:
        if not isinstance(value, self._type):
            return NotImplemented
        return False

    def __repr__(self) -> str:
        return f"<{self._name}>"


ANY_GAME_STATE_ID = _Anything.create(
    name="ANY_GAME_STATE_ID",
    type_=UUID,
    type_hint=GameStateId,
)
