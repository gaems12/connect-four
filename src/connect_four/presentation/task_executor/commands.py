# Copyright (c) 2024, Egor Romanov.
# All rights reserved.
# Licensed under the Personal Use License (see LICENSE).

import logging

from taskiq import TaskiqMessage

from connect_four.application import TryToLoseOnTimeCommand
from connect_four.infrastructure import CommonRetort
from .context_var_setter import ContextVarSetter


_logger = logging.getLogger(__name__)


def try_to_lose_on_time_command_factory(
    message: TaskiqMessage,
    common_retort: CommonRetort,
    context_var_setter: ContextVarSetter,
) -> TryToLoseOnTimeCommand:
    context_var_setter.set()

    _logger.debug(
        {
            "message": "Got taskiq message.",
            "message": message.model_dump(mode="json"),
        },
    )

    try:
        return common_retort.load(message.kwargs, TryToLoseOnTimeCommand)
    except:
        _logger.exception(
            "Error ocurred during converting taskiq message to "
            "TryToLoseOnTimeCommand.",
        )
        raise
