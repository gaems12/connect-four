# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

import json
from typing import Final

from nats.js.client import JetStreamContext

from connect_four.application import (
    GameCreatedEvent,
    GameStartedEvent,
    GameEndedEvent,
    MoveAcceptedEvent,
    MoveRejectedEvent,
    Event,
)
from connect_four.infrastructure.common_retort import CommonRetort


_STREAM: Final = "connect_four"

_EVENT_TO_SUBJECT_MAP: Final = {
    GameCreatedEvent: "game.created",
    GameStartedEvent: "game.started",
    GameEndedEvent: "game.ended",
    MoveAcceptedEvent: "game.move_accepted",
    MoveRejectedEvent: "game.move_rejected",
}


class NATSEventPublisher:
    __slots__ = ("_jetstream", "_common_retort")

    def __init__(
        self,
        jetstream: JetStreamContext,
        common_retort: CommonRetort,
    ):
        self._jetstream = jetstream
        self._common_retort = common_retort

    async def publish(self, event: Event) -> None:
        subject = _EVENT_TO_SUBJECT_MAP[type(event)]

        event_as_dict = self._common_retort.dump(event, dict)
        payload = json.dumps(event_as_dict).encode()

        await self._jetstream.publish(
            subject=subject,
            payload=payload,
            stream=_STREAM,
        )
