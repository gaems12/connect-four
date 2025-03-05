# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

import logging
from uuid import UUID

from taskiq import TaskiqMiddleware, TaskiqMessage

from connect_four.infrastructure import (
    log_extra_context_var,
    OperationId,
    default_operation_id_factory,
)


_logger = logging.getLogger(__name__)


class OperationIdMiddleware(TaskiqMiddleware):
    def pre_execute(self, message: TaskiqMessage) -> TaskiqMessage:
        operation_id = self._extract_operation_id(message)
        self._add_operation_id_to_log_extra(operation_id)

        return message

    def _extract_operation_id(self, message: TaskiqMessage) -> OperationId:
        if not message.args:
            default_operation_id = default_operation_id_factory()

            _logger.warning(
                {
                    "message": (
                        "Takiq message has no operation id. "
                        "Default operation id will be used instead."
                    ),
                    "operation_id": default_operation_id,
                },
            )
            return default_operation_id

        raw_operation_id = message.args[0]
        try:
            return OperationId(UUID(raw_operation_id))
        except:
            default_operation_id = default_operation_id_factory()

            _logger.warning(
                {
                    "message": (
                        "Operation id from takiq message cannot be "
                        "converted to UUID."
                        "Default operation id will be used instead."
                    ),
                    "operation_id": default_operation_id,
                },
                exc_info=True,
            )
            return default_operation_id

    def _add_operation_id_to_log_extra(
        self,
        operation_id: OperationId,
    ) -> None:
        current_log_extra = log_extra_context_var.get().copy()
        current_log_extra["operation_id"] = operation_id
        log_extra_context_var.set(current_log_extra)


class LoggingMiddleware(TaskiqMiddleware):
    def pre_execute(self, message: TaskiqMessage) -> TaskiqMessage:
        _logger.debug(
            {
                "message": "Got taskiq message.",
                "received_message": message.model_dump(mode="json"),
            },
        )
        return message
