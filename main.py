import asyncio
import logging

import aiogram.types
from aiogram.fsm.storage.memory import MemoryStorage
from glQiwiApi import QiwiP2PClient

import settings
import gls

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )

    logger.info("Starting bot")

    gls.bot = aiogram.Bot(
        token=settings.BOT_TOKEN,
        parse_mode='HTML'
    )

    storage = MemoryStorage()
    gls.dispatcher = aiogram.Dispatcher(storage)

    gls.qiwi = QiwiP2PClient(secret_p2p=settings.PAYMENTS_TOKEN)

    from apps.commands import routers
    for router in routers:
        gls.dispatcher.include_router(router)

    try:
        await gls.dispatcher.start_polling(gls.bot)
    finally:
        await gls.dispatcher.storage.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
