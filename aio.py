import asyncio
import aiofiles
from io import BytesIO
from pathlib import Path
from aiohttp import BasicAuth
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.session.aiohttp import AiohttpSession

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth = BasicAuth(login='qaw7Mx', password='4bNrcu')
session = AiohttpSession(proxy=('http://194.67.213.23:9558', auth))

#bot = Bot(token="7170610528:AAG1Pkc8UORSphj8FF0JduIGx-f8SYtp1WQ", session=session)
bot = Bot(token="1700151459:AAF1ZXyRfsl8eSabSMRgcYCVlMCP4RVxRFQ", session=session)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Бот для загрузки файлов на сервера Юсофт")


async def main():
    await dp.start_polling(bot)


@dp.message(F.document)
async def download_document(message: Message, bot: Bot):
    if document := message.document:

        file = BytesIO()
        try:
            await bot.download(document, destination=file)
        except Exception as e:
            logger.error(f"Download file error: {str(e)}")
            await message.answer("Ошибка загрузки файла с серверов Telegram")

        file.seek(0)
        file_path = Path.cwd() / Path('telegram_files') / document.file_name

        try:
            async with aiofiles.open(file_path, "wb") as new_file:
                await new_file.write(file.read())
        except Exception as e:
            logger.error(f"Write file error: {str(e)}")
            await message.answer("Ошибка записи файла на сервер Юсофт")

        logger.info(f"File downloaded: {document.file_name}")
        await message.answer("Файл успешно загружен")


@dp.message(Command("upfiles"))
async def download_chat_files(message: types.Message):
    chat = await bot.get_chat(message.chat.id)
    user = await chat.get_member(message.from_user.id)

    await message.answer('Функция в разработке')

if __name__ == "__main__":
    asyncio.run(main())
