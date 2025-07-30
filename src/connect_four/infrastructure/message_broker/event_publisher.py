# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = ("NATSEventPublisher",)

import json
import logging
from typing import Final

from nats.js.client import JetStreamContext

from connect_four.application import (
    GameCreatedEvent,
    GameEndedEvent,
    MoveAcceptedEvent,
    MoveRejectedEvent,
    Event,
)
from connect_four.infrastructure.common_retort import CommonRetort
from connect_four.infrastructure.operation_id import OperationId


_STREAM: Final = "games"

_EVENT_TO_SUBJECT_MAP: Final = {
    GameCreatedEvent: "gaems12.connect_four.game.created",
    GameEndedEvent: "gaems12.connect_four.game.ended",
    MoveAcceptedEvent: "gaems12.connect_four.game.move_accepted",
    MoveRejectedEvent: "gaems12.connect_four.game.move_rejected",
}

_logger: Final = logging.getLogger(__name__)


class NATSEventPublisher:
    __slots__ = ("_jetstream", "_common_retort", "_operation_id")

    def __init__(
        self,
        jetstream: JetStreamContext,
        common_retort: CommonRetort,
        operation_id: OperationId,
    ):
        self._jetstream = jetstream
        self._common_retort = common_retort
        self._operation_id = operation_id

    async def publish(self, event: Event) -> None:
        subject = _EVENT_TO_SUBJECT_MAP[type(event)]

        event_as_dict = self._common_retort.dump(event)
        event_as_dict["operation_id"] = str(self._operation_id)
        payload = json.dumps(event_as_dict).encode()

        _logger.debug({
            "message": "About to send message to nats.",
            "data": event_as_dict,
        })

        await self._jetstream.publish(
            subject=subject,
            payload=payload,
            stream=_STREAM,
        )
