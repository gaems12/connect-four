# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

import logging
from typing import cast

from faststream.broker.message import StreamMessage

from connect_four.infrastructure import (
    OperationId,
    default_operation_id_factory,
)


_logger = logging.getLogger(__name__)


async def operation_id_factory(message: StreamMessage) -> OperationId:
    decoded_message_body = await message.decode()

    if not isinstance(decoded_message_body, dict):
        default_operation_id = await default_operation_id_factory()
        _logger.warning(
            {
                "message": (
                    "Message received from message broker cannot be "
                    "converted to dict. "
                    "Default operation id will be used instead."
                ),
                "received_message": decoded_message_body,
                "operation_id": default_operation_id,
            },
        )
        return default_operation_id

    decoded_message_body = cast(dict, decoded_message_body)
    operation_id_as_str = decoded_message_body.get("operation_id")
    if not operation_id_as_str:
        default_operation_id = await default_operation_id_factory()
        _logger.warning(
            {
                "message": (
                    "Message receieved from message broker has no "
                    "operation id. "
                    "Default operation id will be used instead."
                ),
                "received_message": decoded_message_body,
                "operation_id": default_operation_id,
            },
        )
        return default_operation_id

    return OperationId(operation_id_as_str)
