from aiogram import Bot, Dispatcher, executor, types
from transliterator import to_cyrillic, to_latin
import unicodedata
import re
import os
import logging

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

async def convert_main(text):
    if (is_latin(text) and has_latin_and_emojis(text)) or not is_cyrillic(text):
        result = to_cyrillic(text)
    else:
        result = to_latin(text)
    return result

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
    result = await convert_main(text)
    await message.reply(result)

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_captions(message: types.Message):
    new_caption = await convert_main(message.caption)
    await bot.send_photo(
      chat_id=message.chat.id,
      photo=message.photo[-1].file_id,
      caption=new_caption)

@dp.message_handler(content_types=types.ContentType.VIDEO)
async def handle_captions(message: types.Message):
    new_caption = await convert_main(message.caption)
    await bot.send_video(
      chat_id=message.chat.id,
      video=message.video.file_id,
      caption=new_caption)

@dp.message_handler(content_types=types.ContentType.AUDIO)
async def handle_captions(message: types.Message):
    new_caption = await convert_main(message.caption)
    await bot.send_audio(
      chat_id=message.chat.id,
      audio=message.audio.file_id,
      caption=new_caption)

@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_document_captions(message: types.Message):
    new_caption = await convert_main(message.caption)
    await bot.send_document(
      chat_id=message.chat.id,
      document=message.document.file_id,
      caption=new_caption)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)