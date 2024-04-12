import aiofiles
from pathlib import Path
from .helper import Helper


class RegistryHelper(Helper):

    async def register_file(self, file_path: str) -> bool:
        try:
            async with aiofiles.open(Path.cwd() / 'downloaded_registry.txt', "a") as registry:
                await registry.write(f"{file_path.split('/')[-1].split('_')[1].split('.')[0]}\n")
        except Exception as e:
            self.logger.warning(f"File registry error: {str(e)}")
            return False
        return True

    @staticmethod
    async def get_registry() -> set[int]:
        async with aiofiles.open(Path.cwd() / 'downloaded_registry.txt', "r") as f:
            return {int(line.rstrip()) async for line in f}
