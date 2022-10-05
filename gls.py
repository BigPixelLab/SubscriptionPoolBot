import aiogram
from glQiwiApi import QiwiP2PClient

bot: aiogram.Bot
dispatcher: aiogram.Dispatcher
qiwi: QiwiP2PClient

__all__ = ('bot', 'dispatcher', 'qiwi')
