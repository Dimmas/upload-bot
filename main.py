import asyncio
from pathlib import Path
from aiohttp import BasicAuth
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram import Bot, Dispatcher, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.client.session.aiohttp import AiohttpSession
from helpers import FileHelper, RegistryHelper

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ADMIN_GROUP = ('usoft_ru', 'dimmas_bobrov')

auth = BasicAuth(login='qaw7Mx', password='4bNrcu')
session = AiohttpSession(proxy=('http://194.67.213.23:9558', auth))

bot = Bot(token="7170610528:AAG1Pkc8UORSphj8FF0JduIGx-f8SYtp1WQ", session=session)
dp = Dispatcher()

file_helper = FileHelper(bot, logger)
registry_helper = RegistryHelper(bot, logger)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Бот для загрузки файлов на сервера Юсофт")


async def main():
    await dp.start_polling(bot)


@dp.message(F.document)
async def download_document(message: Message, bot: Bot):
    if document := message.document:
        if 'pdf' not in document.file_name:
            await message.answer("Поддерживается обработка только pdf файлов")
            return

        try:
            file_info = await bot.get_file(document.file_id)
        except TelegramBadRequest as tge:
            logger.warning(f"Get file information error: {str(tge)}")
            return

        file = await file_helper.download_file(file_info.file_path)
        if not file:
            await message.answer("Ошибка загрузки файла с серверов Telegram")
            return

        file_path = Path.cwd() / Path('telegram_files') / document.file_name

        if not await file_helper.save_file(file_path, file):
            await message.answer("Ошибка записи файла на сервер Юсофт")
            return

        await registry_helper.register_file(file_info.file_path)
        await message.answer("Файл успешно загружен")


@dp.message(Command("upfiles"))
async def download_chat_files(message: types.Message):
    if message.from_user.username not in ADMIN_GROUP:
        await message.answer('Доступ запрещен')
        return

    file_registry = await registry_helper.get_registry()
    total_files = {i for i in range(max(file_registry))}
    delta = total_files - file_registry

    if len(delta) == 0:
        await message.answer('Все файлы загружены на сервер')
        return

    for index in delta:
        file = await file_helper.download_file(f'documents/file_{index}.pdf')
        if not file:
            continue

        file_path = Path.cwd() / Path('telegram_files') / f'file_{index}.pdf'

        if not await file_helper.save_file(file_path, file):
            await message.answer('Ошибка сохранения файлов на сервер Юсофт')
            return
        if not await registry_helper.register_file(f'documents/file_{index}.pdf'):
            await message.answer('Ошибка регистрации загруженных файлов на сервере Юсофт')
            return

    await message.answer('Подгрузка документов выполнена')

if __name__ == "__main__":
    asyncio.run(main())
