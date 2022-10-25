import asyncio
import logging

import aiogram.types
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile

import settings
import gls
from utils import database

logger = logging.getLogger(__name__)

PHOTO, DOCUMENT = range(2)


# Токен бота, который будет использован для загрузки
# (не имеет особого значения, главное чтобы был действительным)
BOT_TOKEN = settings.BOT_TOKEN

# Чат в который будут отправлены файлы
# (опять-таки не имеет особого значения, telegram так устроен, что нам
# нужно отправить куда-то файл, чтобы получить его id)
SPAM_CHAT = 1099569178

# Ресурсы для загрузки, в формате: (тип, путь, имя, запрос)
# Тип - PHOTO или DOCUMENT
# Путь - путь к файлу относительно директории проекта.
# Имя - имя, которое будет передано telegram-у (таким именем будет обладать файл на сервере).
# Запрос - запрос к базе данных, который будет выполнен после успешной загрузки файла,
#       получает file_id в качестве аргумента
RESOURCES = [
    (DOCUMENT, 'resources/NETFLIX-BOUGHT.mp4', 'NETFLIX-BOUGHT.mp4',
     """ update "Service" set bought = %(file_id)s where name = 'netflix' """),

    (DOCUMENT, 'resources/SPOTIFY-BOUGHT.mp4', 'SPOTIFY-BOUGHT.mp4',
     """ update "Service" set bought = %(file_id)s where name = 'spotify' """),

    (PHOTO, 'resources/NETFLIX-BANNER.jpg', 'NETFLIX-BANNER.jpg',
     """ update "Service" set banner = %(file_id)s where name = 'netflix' """),

    (PHOTO, 'resources/SPOTIFY-BANNER.jpg', 'SPOTIFY-BANNER.jpg',
     """ update "Service" set banner = %(file_id)s where name = 'spotify' """),

    (PHOTO, 'resources/INTRO.jpg', 'INTRO.jpg', None),
]


async def on_startup():
    methods = {
        DOCUMENT: (gls.bot.send_document, lambda m: m.document.file_id),
        PHOTO: (gls.bot.send_photo, lambda m: m.photo[0].file_id)
    }

    for i, (_type, path, name, query) in enumerate(RESOURCES):
        await gls.bot.send_message(SPAM_CHAT, f'UPLOADING "{name}" ({i + 1}/{len(RESOURCES)})...')

        send_stuff, extract_file_id = methods[_type]

        try:
            message = await send_stuff(SPAM_CHAT, FSInputFile(path, name))
        except TelegramBadRequest:
            await gls.bot.send_message(SPAM_CHAT, 'Failed to upload resource')
            continue

        file_id = extract_file_id(message)

        if query:
            database.execute(query, query % {'file_id': file_id}, file_id=file_id)

        await gls.bot.send_message(SPAM_CHAT, f'<code>{file_id}</code>')

    await gls.bot.send_message(SPAM_CHAT, 'Done.')


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )

    logger.info("Starting bot")

    gls.bot = aiogram.Bot(
        token=BOT_TOKEN,
        parse_mode='HTML'
    )

    storage = MemoryStorage()
    gls.dispatcher = aiogram.Dispatcher(storage)
    gls.dispatcher.startup()(on_startup)

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
