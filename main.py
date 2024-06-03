import asyncio
from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from motor.motor_asyncio import AsyncIOMotorClient
import pyromod
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
mongo_uri = os.getenv("DATABASE_URL")
db_name = os.getenv("DATABASE_NAME", "word_replacer")


# Database class for MongoDB interactions
class Database:
    def __init__(self, uri):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db["words"]

    async def add_word(self, category, word, replacement=None):
        await self.collection.update_one(
            {"category": category, "word": word},
            {"$set": {"replacement": replacement}},
            upsert=True,
        )

    async def remove_word(self, category, word):
        await self.collection.delete_one({"category": category, "word": word})

    async def get_words(self, category):
        cursor = self.collection.find({"category": category})
        return {
            doc["word"]: doc.get("replacement")
            for doc in await cursor.to_list(length=None)
        }


# Initialize Pyrogram Client and Database
app = Client("word_replacer_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
db = Database(mongo_uri)


# Start command
@app.on_message(filters.command("start") & filters.private)
async def start(client, message: Message):
    replace_words = await db.get_words("replace")
    remove_words = await db.get_words("remove")

    text = "✨ Welcome to the Word Replacer Bot! ✨\n\n"
    text += "🔄 **Replace Words**:\n"
    for word, replacement in replace_words.items():
        text += f"`{word}` ➡️ `{replacement}`\n"

    text += "\n❌ **Remove Words**:\n"
    for word in remove_words:
        text += f"`{word}`\n"
    text += "\nUse /addword to add or update words and /removeword to remove words."
    await message.reply_text(text)


# Command to add or update words
@app.on_message(filters.command("addword") & filters.private)
async def add_word(client, message: Message):
    category_buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔄 Replace Words", callback_data="add_replace")],
            [InlineKeyboardButton("❌ Remove Words", callback_data="add_remove")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")],
        ]
    )
    await message.reply_text("Choose the category:", reply_markup=category_buttons)


@app.on_callback_query(filters.regex(r"add_(replace|remove)"))
async def process_add_word(client, callback_query):
    category = "replace" if "replace" in callback_query.data else "remove"

    category_words = await db.get_words(category)

    text = "Send the word you want to add.\n\n"
    text += "📜 **Words in the selected category**:\n"
    for word in category_words:
        text += f"\n`{word}`"
    text += "\n\nType /cancel to cancel."
    try:
        word_msg = await client.ask(callback_query.message.chat.id, text)

        if word_msg.text == "/cancel":
            await callback_query.message.reply_text(
                "❌ Cancelled.", reply_markup=back_button()
            )
            return

        if category == "replace":
            replacement_msg = await client.ask(
                callback_query.message.chat.id, "Send the replacement word."
            )
            await db.add_word(category, word_msg.text, replacement_msg.text)
        else:
            await db.add_word(category, word_msg.text)
        await callback_query.message.reply_text(
            "✅ Word added successfully.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
            ),
        )
    except Exception as e:
        await callback_query.message.reply_text(f"❌ An error occurred: {e}")


# Command to remove words
@app.on_message(filters.command("removeword") & filters.private)
async def remove_word(client, message: Message):
    category_buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔄 Replace Words", callback_data="remove_replace")],
            [InlineKeyboardButton("❌ Remove Words", callback_data="remove_remove")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")],
        ]
    )
    await message.reply_text("Choose the category:", reply_markup=category_buttons)


@app.on_callback_query(filters.regex(r"remove_(replace|remove)"))
async def process_remove_word(client, callback_query):
    category = "replace" if "replace" in callback_query.data else "remove"
    try:
        words = await db.get_words(category)
        text = "📜 **Words in the selected category**:\n\n"
        for i, word in enumerate(words.keys(), 1):
            text += f"`{i}) {word}`\n"

        await callback_query.message.reply_text(text)

        word_msg = await client.ask(
            callback_query.message.chat.id,
            "Send the word number you want to remove\n\nExample: 1\n\nType /cancel to cancel.",
        )
        if word_msg.text == "/cancel":
            await callback_query.message.reply_text(
                "❌ Cancelled.", reply_markup=back_button()
            )
            return

        word_list = list(words.keys())
        word_to_remove = word_list[int(word_msg.text) - 1]
        await db.remove_word(category, word_to_remove)
        await callback_query.message.reply_text(
            "✅ Word removed successfully.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
            ),
        )
    except Exception as e:
        await callback_query.message.reply_text(f"❌ An error occurred: {e}")


# Batch processing command
@app.on_message(filters.command("batch") & filters.private)
async def batch_process(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /batch <channel_id>")
        return

    if not message.command[1].replace("-", "").isdigit():
        await message.reply_text("Invalid channel ID.")
        return

    channel_id = int(message.command[1])

    try:
        chat = await client.get_chat(channel_id)
        txt = await client.send_message(channel_id, ".")
        last_message_id = txt.id
        total_messages = range(1, last_message_id)
        output = await message.reply_text("🔄 Processing messages...")
        for i in range(0, len(total_messages), 200):
            channel_posts = await client.get_messages(
                channel_id, total_messages[i : i + 200]
            )

            for post in channel_posts:
                text = og_text = post.text or post.caption
                post: Message
                if not text:
                    continue

                if post.forward_from:
                    continue

                text = text.html
                replace_words = await db.get_words("replace")
                remove_words = await db.get_words("remove")

                for word, replacement in replace_words.items():
                    text = text.replace(word, replacement)
                for word in remove_words:
                    text = text.replace(word, "")

                if text == og_text:
                    continue

                try:
                    if not text and post.text:
                        await handle_floodwait(post.edit_text, ".")
                        continue

                    if post.text:
                        await handle_floodwait(post.edit_text, text)
                    else:
                        await handle_floodwait(post.edit_caption, text)
                except Exception as e:
                    print(f"An error occurred: {e}")
                    continue

        await output.edit_text("✅ Batch processing completed.")
    except Exception as e:
        await output.edit_text(f"❌ An error occurred: {e}")


async def handle_floodwait(func, *args, **kwargs):
    try:
        await func(*args, **kwargs)
    except errors.FloodWait as e:
        await asyncio.sleep(e.value)
        await handle_floodwait(func, *args, **kwargs)


# Process incoming messages
@app.on_message((filters.text | filters.caption) & filters.private)
async def process_message(client, message: Message):
    text = message.text or message.caption
    replace_words = await db.get_words("replace")
    remove_words = await db.get_words("remove")

    for word, replacement in replace_words.items():
        text = text.replace(word, replacement)
    for word in remove_words:
        text = text.replace(word, "")

    if message.text:
        await message.reply_text(text)
    else:
        await message.reply_text(text, reply_markup=message.reply_markup)


# Handle back button
@app.on_callback_query(filters.regex(r"back"))
async def go_back(client, callback_query):
    await start(client, callback_query.message)


def back_button():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
    )

print("Bot started!")
# Run the bot
app.run()
