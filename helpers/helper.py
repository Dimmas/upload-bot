from aiogram import Bot
from logging import Logger


class Helper:
    def __init__(self, bot: Bot, logger: Logger):
        self.bot = bot
        self.logger = logger
