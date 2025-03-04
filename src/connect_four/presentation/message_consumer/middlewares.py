# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

import logging
from uuid import UUID
from typing import Any

from faststream import BaseMiddleware
from faststream.broker.message import StreamMessage

from connect_four.infrastructure import (
    log_extra_context_var,
    OperationId,
    default_operation_id_factory,
)


_logger = logging.getLogger(__name__)


class OperationIdMiddleware(BaseMiddleware):
    async def on_consume[T: Any = Any](
        self,
        msg: StreamMessage[T],
    ) -> StreamMessage[T]:
        operation_id = await self._extract_operation_id(msg)
        self._set_operation_id_to_log_extra_context_var(operation_id)

        return await super().on_consume(msg)

    async def _extract_operation_id(
        self,
        message: StreamMessage,
    ) -> OperationId:
        decoded_message = await message.decode()

        if not isinstance(decoded_message, dict):
            default_operation_id = default_operation_id_factory()
            _logger.warning(
                {
                    "message": (
                        "Message received from message broker cannot be "
                        "converted to dict. "
                        "Default operation id will be used instead."
                    ),
                    "operation_id": default_operation_id,
                },
            )
            return default_operation_id

        raw_operation_id = decoded_message.get("operation_id")
        if not raw_operation_id:
            default_operation_id = default_operation_id_factory()
            _logger.warning(
                {
                    "message": (
                        "Message receieved from message broker has no "
                        "operation id. "
                        "Default operation id will be used instead."
                    ),
                    "operation_id": default_operation_id,
                },
            )
            return default_operation_id

        try:
            return OperationId(UUID(raw_operation_id))
        except:
            default_operation_id = default_operation_id_factory()
            _logger.warning(
                {
                    "message": (
                        "Operation id from message received from "
                        "message broker cannot be converted to UUID."
                        "Default operation id will be used instead."
                    ),
                    "operation_id": default_operation_id,
                },
                exc_info=True,
            )
            return default_operation_id

    def _set_operation_id_to_log_extra_context_var(
        self,
        operation_id: OperationId,
    ) -> None:
        current_log_extra = log_extra_context_var.get().copy()
        current_log_extra["operation_id"] = operation_id
        log_extra_context_var.set(current_log_extra)


class LoggingMiddleware(BaseMiddleware):
    async def on_consume[T: Any = Any](
        self,
        msg: StreamMessage[T],
    ) -> StreamMessage[T]:
        decoded_message = await msg.decode()

        _logger.debug(
            {
                "message": "Got message from message broker.",
                "decoded_message": decoded_message,
            },
        )

        if not decoded_message or not isinstance(decoded_message, dict):
            error_message = (
                "Decoded message from message broker cannot be "
                "converted to dict.",
            )
            _logger.error(error_message)

            raise Exception(error_message)

        return await super().on_consume(msg)
