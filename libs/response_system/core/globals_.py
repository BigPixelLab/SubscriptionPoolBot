from __future__ import annotations

import contextvars
import datetime

import aiogram.types

# Open variables
global_time: contextvars.ContextVar[datetime.datetime | None] = \
    contextvars.ContextVar('global_time', default=None)

# In-lib use only
message: contextvars.ContextVar[aiogram.types.Message | None] = \
    contextvars.ContextVar('message', default=None)
