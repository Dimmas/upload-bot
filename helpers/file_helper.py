import aiofiles
from io import BytesIO
from pathlib import Path
from .helper import Helper


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
        try:
            async with aiofiles.open(file_path, "wb") as new_file:
                await new_file.write(file.read())
        except Exception as e:
            self.logger.error(f"Write file error: {str(e)}")
            return False
        return True
