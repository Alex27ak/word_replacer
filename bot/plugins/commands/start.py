from pyrogram import Client, filters
from pyrogram.types import Message
from bot.config import Script
from bot.utils.helpers import add_user


@Client.on_message(filters.command("start") & filters.private & filters.incoming)
async def start(bot: Client, message: Message):
    await add_user(message.from_user.id)
    await message.reply_text(
        Script.START_MESSAGE, disable_web_page_preview=True, quote=True
    )
