# Copyright (c) 2024, Egor Romanov.
# All rights reserved.

import json

from nats.js.client import JetStreamContext

from four_in_a_row.application import GameCreatedEvent, Event


_GAME_CREATED_SUBJECT = "game.created"


class NATSEventPublisher:
    __all__ = ("_jetstream",)

    def __init__(self, jetstream: JetStreamContext):
        self._jetstream = jetstream

    async def publish(self, event: Event) -> None:
        if isinstance(event, GameCreatedEvent):
            await self._publish_game_created(event)

    async def _publish_game_created(
        self,
        event: GameCreatedEvent,
    ) -> None:
        event_as_dict = {
            "id": event.id.hex,
            "players": map(lambda user_id: user_id.hex, event.players),
            "current_turn": event.current_turn.hex,
        }
        await self._jetstream.publish(
            _GAME_CREATED_SUBJECT,
            payload=json.dumps(event_as_dict).encode(),
        )
