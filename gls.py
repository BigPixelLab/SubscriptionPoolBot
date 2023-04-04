import typing

import aiogram
import peewee
from aiogram.fsm.storage.base import BaseStorage
from glQiwiApi import QiwiP2PClient

bot: aiogram.Bot
operator_bot: aiogram.Bot
storage: BaseStorage

qiwi: QiwiP2PClient

BaseModel: typing.Type[peewee.Model]
db: peewee.PostgresqlDatabase

__all__ = (
    'bot',
    'operator_bot',
    'storage',
    'qiwi',
    'BaseModel'
)
