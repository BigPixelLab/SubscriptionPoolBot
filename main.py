""" ... """
import asyncio
import logging
import sys

import aiogram.types
import peewee
from aiogram.fsm.storage.memory import MemoryStorage
from glQiwiApi import QiwiP2PClient

import response_system
import settings
import gls
import template
import userdata
from template.syntax.telegram import TELEGRAM

logger = logging.getLogger(__name__)


def get_BaseModel(db):
    """ Функция возвращающая базовую модель peewee
       для переданной базы данных """

    class BaseModel(peewee.Model):
        """ Базовая модель """

        # noinspection PyMissingOrEmptyDocstring
        class Meta:
            database = db

    return BaseModel


async def main():
    """ Точка входа в программу """

    logging.basicConfig(level=settings.LOGGING_LEVEL, format=settings.LOGGING_FORMAT)
    logger.info("Starting bot")

    template.set_default_syntax(TELEGRAM)

    # noinspection PyUnresolvedReferences
    import template_extensions

    # Добавляем папки с библиотеками и модулями в path
    sys.path.extend(settings.LIBS)

    # Инициализация ботов
    gls.storage = MemoryStorage()
    userdata.__storage__ = gls.storage

    gls.bot = aiogram.Bot(token=settings.BOT_TOKEN, parse_mode=settings.DEFAULT_PARSE_MODE)
    dispatcher = aiogram.Dispatcher(gls.storage)
    dispatcher.message.middleware(
        response_system.middleware.MessageResponseMiddleware()
    )
    dispatcher.callback_query.middleware(
        response_system.middleware.CallbackQueryResponseMiddleware()
    )

    gls.operator_bot = aiogram.Bot(token=settings.OPERATOR_BOT_TOKEN, parse_mode=settings.DEFAULT_PARSE_MODE)
    operator_dispatcher = aiogram.Dispatcher(gls.storage)
    operator_dispatcher.message.middleware(
        response_system.middleware.MessageResponseMiddleware()
    )
    operator_dispatcher.callback_query.middleware(
        response_system.middleware.CallbackQueryResponseMiddleware()
    )

    # Инициализация клиента qiwi
    gls.qiwi = QiwiP2PClient(secret_p2p=settings.PAYMENTS_TOKEN)

    # Инициализация подключения к базе данных
    gls.db = peewee.PostgresqlDatabase(settings.DATABASE_URI)
    gls.BaseModel = get_BaseModel(gls.db)

    # Подключаем router-ы
    from apps.routers import routers
    for router in routers:
        dispatcher.include_router(router)

    from apps.routers import operator_routers
    for router in operator_routers:
        operator_dispatcher.include_router(router)

    @dispatcher.callback_query(aiogram.F.data == 'delete-this')
    @operator_dispatcher.callback_query(aiogram.F.data == 'delete-this')
    async def delete_this_handler(_):
        """ Handler для удаления сообщения, которое он обрабатывает """
        return response_system.delete_original()

    # Запускаем ботов
    await asyncio.gather(
        dispatcher.start_polling(gls.bot),
        operator_dispatcher.start_polling(gls.operator_bot)
    )


if __name__ == '__main__':
    asyncio.run(main())
