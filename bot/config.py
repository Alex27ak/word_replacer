import os
from dotenv import load_dotenv

load_dotenv()


def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default


class Config(object):
    API_ID = int(os.environ.get("API_ID"))
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "tg_bot")
    DATABASE_URL = os.environ.get("DATABASE_URL", None)
    OWNER_ID = int(os.environ.get("OWNER_ID"))
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))
    WEB_SERVER = is_enabled(os.environ.get("WEB_SERVER", "False"), False)


class Script(object):
    START_MESSAGE = os.environ.get("START_MESSAGE", "Start message")
    DEV_MESSAGE = """👋 Hey there, I'm Kevin Nadar – your go-to Telegram bot developer!

🤖 Love having bots that do the heavy lifting for you? That's my jam! I'm all about crafting super cool and custom Telegram bots that make your life a breeze.

✨ **What I Do**

- **Bot Magic:** From automating tasks to interactive games, I create bots that do it all. Seriously, ask me anything!
- **Tailored to You:** Your bot, your rules. I'll whip up a bot that's as unique as you are.
- **Chill Vibes:** I keep your data super safe, so you can relax and enjoy the bot party.
- **Always Improving:** Telegram evolves, and my bots grow with it. I'm here to keep things fresh and fab.

Ready for your own bot buddy? Ping me on [Telegram](https://telegram.me/ask_admin001) or check out my tricks on [GitHub](https://github.com/kevinnadar22). Wanna hire me? Find me on [Fiverr](https://www.fiverr.com/kevin264_)!

Let's bot up and have some fun! 🤘"""
    HELP_MESSAGE = os.environ.get("HELP_MESSAGE", "Help message")
