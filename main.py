import asyncio
from pathlib import Path
from aiohttp import BasicAuth
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram import Bot, Dispatcher, types, F
from helpers import FileHelper, RegistryHelper
from aiogram.client.session.aiohttp import AiohttpSession

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ADMIN_GROUP = ('usoft_ru', 'dimmas_bobrov')

auth = BasicAuth(login='qaw7Mx', password='4bNrcu')
session = AiohttpSession(proxy=('http://194.67.213.23:9558', auth))

#bot = Bot(token="7170610528:AAG1Pkc8UORSphj8FF0JduIGx-f8SYtp1WQ", session=session) # Белый ворон
bot = Bot(token="1700151459:AAF1ZXyRfsl8eSabSMRgcYCVlMCP4RVxRFQ", session=session)
dp = Dispatcher()

file_helper = FileHelper(bot, logger)
registry_helper = RegistryHelper(bot, logger)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Бот для загрузки файлов на сервера Юсофт")


async def main():
    await dp.start_polling(bot)


@dp.message(F.photo)
async def download_photo(message: Message, bot: Bot):

    @file_helper.download(message, bot)
    async def download():
        if photo := message.photo[-1]:
            return photo.file_id, photo.file_unique_id

    if file_path := await download():
        await registry_helper.register_file(file_path, 'photos')
        await message.answer("Фото успешно загружено")


@dp.message(F.document)
async def download_document(message: Message, bot: Bot):
    @file_helper.download(message, bot)
    async def download():
        if document := message.document:
            return document.file_id, document.file_name.split('.')[0]

    if file_path := await download():
        await registry_helper.register_file(file_path, 'documents')
        await message.answer("Файл успешно загружен")


@dp.message(Command("upfiles"))
async def download_chat_files(message: types.Message):
    if message.from_user.username not in ADMIN_GROUP:
        await message.answer('Доступ запрещен')
        return

    for registry in ('documents', 'photos'):
        file_registry = await registry_helper.get_registry(registry)
        total_files = {i for i in range(max(file_registry) if file_registry else 1000)}
        delta = total_files - file_registry

        if len(delta) == 0:
            await message.answer(f'{registry}: Все файлы уже загружены на сервер')
            return

        for index in delta:
            for extention in ['jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx']:
                file_name = f'file_{index}.{extention}'
                if file := await file_helper.download_file(f'{registry}/{file_name}'):
                    break

            if not file:
                continue

            file_path = Path.cwd() / Path('saved_files') / registry / file_name

            if not await file_helper.save_file(file_path, file):
                await message.answer('Ошибка сохранения файлов на сервер Юсофт')
                return
            if not await registry_helper.register_file(f'{registry}/{file_name}', registry):
                await message.answer('Ошибка регистрации загруженных файлов на сервере Юсофт')
                return

    await message.answer('Подгрузка файлов выполнена')

if __name__ == "__main__":
    asyncio.run(main())
