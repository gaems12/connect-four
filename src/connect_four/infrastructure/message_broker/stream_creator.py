# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

from nats.js import JetStreamContext
from nats.js.api import StreamConfig


class NATSStreamCreator:
    __slots__ = ("_jetstream",)

    def __init__(self, jetstream: JetStreamContext):
        self._jetstream = jetstream

    async def create(self) -> None:
        games_stream_config = StreamConfig(
            name="games",
            subjects=[
                "connect_four.game.created",
                "connect_four.game.started",
                "connect_four.game.ended",
                "connect_four.game.move_accepted",
                "connect_four.game.move_rejected",
                "connection_hub.game.created",
                "connection_hub.game.ended",
                "api_gateway.game.move_was_made",
            ],
        )
        await self._jetstream.add_stream(games_stream_config)
