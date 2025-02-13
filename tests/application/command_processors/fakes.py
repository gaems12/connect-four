# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

from connect_four.domain import GameId, UserId, Game
from connect_four.application import (
    SortGamesBy,
    GameGateway,
    Event,
    EventPublisher,
)


class FakeGameGateway(GameGateway):
    __slots__ = ("_games",)

    def __init__(self, games: dict[GameId, Game]):
        self._games = games

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
                "FakeGameGateway. Cannot list by player ids: "
                "limit is not a positive number or zero.",
            )

        return games

    async def save(self, game: Game) -> None:
        self._games[game.id] = game

    async def update(self, game: Game) -> None:
        self._games[game.id] = game


class FakeEventPublisher(EventPublisher):
    __slots__ = ("_events",)

    def __init__(self, events: list[Event]):
        self._events = events

    @property
    def events(self) -> list[Event]:
        return self._events

    async def publish(self, event: Event) -> None:
        self._events.append(event)
