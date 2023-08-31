from aiogram import Bot, Dispatcher, executor, types
from transliterator import to_cyrillic, to_latin
import unicodedata
import re
import os
import fcntl
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import logging

logging.basicConfig(level=logging.INFO)

class BotSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.bot = Bot(token=BOT_TOKEN, parse_mode="html")
            cls._instance.dp = Dispatcher(cls._instance.bot, storage=MemoryStorage())
        return cls._instance

try:
    # Try acquiring an exclusive lock on the lock file
    fcntl.lockf(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

    # Only continue if the lock is acquired successfully
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    bot_singleton = BotSingleton()
    bot = bot_singleton.bot
    dp = bot_singleton.dp

    @dp.message_handler(commands=['start', 'help'])
    async def send_welcome(message: types.Message):
        await message.reply("Salom! Bu Alifbo Konvertori matnlarni Lotinchada Krillchaga va aksincha oʻgirib beradi!")

    def is_latin(text):
        """Checks if the given text is in the Latin alphabet"""
        for char in text:
            if unicodedata.category(char) != 'Ll' and unicodedata.category(char) != 'Lu':
                return False
        return True

    def has_latin_and_emojis(text):
        """Checks if the given text contains latin letters and emojis"""
        latin_pattern = r'[a-zA-Z]'
        emoji_pattern = r'[^\w\s,]'

        has_latin = bool(re.search(latin_pattern, text))
        has_emoji = bool(re.search(emoji_pattern, text))
        
        return has_latin and has_emoji

    def is_cyrillic(text):
        """Checks if the given text is in the Cyrillic alphabet"""
        cyrillic_pattern = re.compile(r'[\u0400-\u04FF]')
        return bool(cyrillic_pattern.search(text))

    @dp.message_handler()
    async def convert(message: types.Message):
        text = message.text
        if (is_latin(text) and has_latin_and_emojis(text)) or not is_cyrillic(text):
            result = to_cyrillic(text)
        else:
            result = to_latin(text)

        await message.reply(result)

    if __name__ == '__main__':
        executor.start_polling(dp, skip_updates=True)
finally:
    # Release the lock and close the lock file
    fcntl.lockf(lock_fd, fcntl.LOCK_UN)
    lock_fd.close()