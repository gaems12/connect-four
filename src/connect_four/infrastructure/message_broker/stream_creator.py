# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

__all__ = ("NATSStreamCreator",)

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
                "gaems12.connect_four.game.created",
                "gaems12.connect_four.game.ended",
                "gaems12.connect_four.game.move_accepted",
                "gaems12.connect_four.game.move_rejected",
                "gaems12.connection_hub.connect_four.game.created",
                "gaems12.connection_hub.connect_four.game.player_disqualified",
                "gaems12.api_gateway.connect_four.game.move_was_made",
            ],
        )
        await self._jetstream.add_stream(games_stream_config)
