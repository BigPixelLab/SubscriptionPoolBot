""" ... """
import asyncio
import datetime
import logging
import os
import sys

import aiogram.types
import peewee
from aiogram.fsm.state import any_state
from aiogram.fsm.storage.memory import MemoryStorage
from glQiwiApi import QiwiP2PClient

import settings
# Добавляем папки с библиотеками и модулями в path
sys.path.extend(settings.LIBS)

import ezqr
import response_system
import response_system.core.responses
import gls
import template
import userdata
from template_for_aiogram import aiogram_syntax

logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)


def get_BaseModel(db):
    """ Функция возвращающая базовую модель peewee
       для переданной базы данных """

    class BaseModel(peewee.Model):
        """ Базовая модель """

        class Meta:
            database = db

        @classmethod
        def select_by_id(cls, pk):
            return cls.select().where(cls._meta.primary_key == pk)

    return BaseModel


def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


async def main():
    """ Точка входа в программу """

    os.makedirs(settings.LOGGING_DIRECTORY, exist_ok=True)

    logging_filename = os.path.join(
        settings.LOGGING_DIRECTORY,
        datetime.datetime.now().strftime(
            settings.LOGGING_FILENAME_FORMAT
        )
    )

    logging.basicConfig(
        level=settings.LOGGING_LEVEL,
        format=settings.LOGGING_FORMAT,
        filename=logging_filename,
        filemode='a'
    )

    sys.excepthook = log_uncaught_exceptions

    logger.info("Starting bot")
    print("Starting bot")

    template.set_default_syntax(aiogram_syntax)

    response_system.core.responses.__debugging__ = settings.DEBUG

    # noinspection PyUnresolvedReferences
    import template_extensions

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
    ezqr.set_default_db(gls.db)

    # Подключаем router-ы
    from apps.routers import routers
    for router in routers:
        dispatcher.include_router(router)

    from apps.routers import operator_routers
    for router in operator_routers:
        operator_dispatcher.include_router(router)

    @dispatcher.callback_query(any_state, aiogram.F.data == 'delete-this')
    @operator_dispatcher.callback_query(any_state, aiogram.F.data == 'delete-this')
    async def delete_this_handler(_):
        """ Handler для удаления сообщения, которое он обрабатывает """
        return response_system.delete()

    # Разрешаем циклические зависимости в базе данных
    for model in gls.BaseModel.__subclasses__():
        peewee.DeferredForeignKey.resolve(model)

    # Инициализация событий
    # noinspection PyUnresolvedReferences
    import events

    # Запускаем ботов
    await asyncio.gather(
        dispatcher.start_polling(gls.bot),
        operator_dispatcher.start_polling(gls.operator_bot)
    )


if __name__ == '__main__':
    asyncio.run(main())
