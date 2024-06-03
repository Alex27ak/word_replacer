from pyrogram import Client, filters
from database import db
from bot.config import Config


@Client.on_message(
    filters.command("users", prefixes="/")
    & filters.user(Config.OWNER_ID)
    & filters.incoming
)
async def users(client, message):
    users_list = await db.users.get_all_users()
    user_ids = [user["_id"] for user in users_list]
    if users_list:
        tg_users = await client.get_users(user_ids, raise_error=False)
        users = "".join(f"`{user.id}` - {user.mention}\n" for user in tg_users)
        await message.reply_text(
            f"**Total Users:**\n\n{users}\n**Total Users Count:** {len(users_list)}"
        )

    else:
        await message.reply_text(f"**Total Users:**\n\nNo Users")
