# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

import logging
from uuid import UUID

from taskiq import TaskiqMessage

from connect_four.infrastructure import (
    OperationId,
    default_operation_id_factory,
)


_logger = logging.getLogger(__name__)


def operation_id_factory(message: TaskiqMessage) -> OperationId:
    raw_operation_id = message.kwargs.get("operation_id")
    if not raw_operation_id:
        default_operation_id = default_operation_id_factory()
        _logger.warning(
            {
                "message": (
                    "Taskiq message has no operation id. "
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
                    "Operation id from taskiq message cannot be converted "
                    "to UUID. Default operation id will be used instead."
                ),
                "operation_id": default_operation_id,
            },
            exc_info=True,
        )
        return default_operation_id
