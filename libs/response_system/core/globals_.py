from __future__ import annotations

import contextvars
import datetime

import aiogram.types

from .responses import Response

# Open variables
global_time: contextvars.ContextVar[datetime.datetime | None] = \
    contextvars.ContextVar('global_time', default=None)

# In-lib use only
message_var: contextvars.ContextVar[aiogram.types.Message | None] = \
    contextvars.ContextVar('message_var', default=None)

response_var: contextvars.ContextVar[Response | None] = \
    contextvars.ContextVar('response_var', default=None)
