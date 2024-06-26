import aiofiles
from io import BytesIO
from aiogram import Bot
from pathlib import Path
from .helper import Helper
from functools import wraps
from redis.asyncio import from_url
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest
from aiofiles import os as aio_os


redis = from_url("redis://172.17.0.2", encoding="utf8", decode_responses=True)


class FileHelper(Helper):

    async def download_file(self, file_path: str) -> bool | BytesIO:
        file = BytesIO()
        try:
            await self.bot.download_file(file_path, destination=file)
        except Exception as e:
            self.logger.error(f"Download file error: {str(e)}")
            return False
        return file

    async def save_file(self, file_path: Path, file: BytesIO) -> bool:
        file.seek(0)

        cat_path = list(file_path.parents)[0]
        await aio_os.makedirs(cat_path, exist_ok=True)

        # Защита от перезаписи файлов при назывании их одним именем
        path = file_path
        try:
            await aio_os.stat(file_path)
            for i in range(50):
                file_name = f'{i}_{file_path.name}'
                path = Path(cat_path, file_name)
                await aio_os.stat(path)
            self.logger.error(f"Превышен лимит для одноименных файлов: {file_name}")
            return False
        except:
            pass

        try:
            async with aiofiles.open(path, "wb") as new_file:
                await new_file.write(file.read())
        except Exception as e:
            self.logger.error(f"Write file error: {str(e)}")
            return False
        return True

    def download(self, message: Message, bot: Bot):

        def _download(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    file_id, file_name = await func(*args, **kwargs)
                except Exception as err:
                    self.logger.error(str(err))
                    return
                try:
                    file_info = await bot.get_file(file_id)
                except TelegramBadRequest as tge:
                    self.logger.warning(f"Get file information error: {str(tge)}")
                    return

                file = await self.download_file(file_info.file_path)
                if not file:
                    await message.answer("Ошибка загрузки файла с серверов Telegram")
                    return

                file_extention = file_info.file_path.split('.')[-1]

                if message.caption:
                    file_name = message.caption.replace(' ', '_')

                async with redis.client() as conn:
                    if message.media_group_id and not await conn.get(f'counter_{message.media_group_id}'):
                        await conn.set(message.media_group_id, file_name)
                        await conn.set(f'counter_{message.media_group_id}', 1)
                        file_name = f'{file_name}_0'

                if file_extention not in file_name:
                    file_name = f"{file_name}.{file_extention}"

                if message.media_group_id and not message.caption:
                    async with redis.client() as conn:
                        file_name = await conn.get(message.media_group_id)
                        file_name = f"{file_name}_{await conn.get(f'counter_{message.media_group_id}')}.{file_extention}"
                        await conn.incr(f'counter_{message.media_group_id}')

                if message.from_user.first_name:
                    file_path = Path('telegram_files', message.from_user.first_name, file_name)
                else:
                    file_path = Path('telegram_files', file_name)

                if not await self.save_file(file_path, file):
                    await message.answer("Ошибка записи файла на сервер Юсофт")
                    return

                self.logger.info({'from': message.from_user.first_name, 'file_name': file_name})
                return file_info.file_path

            return wrapper
        return _download
