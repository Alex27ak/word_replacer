import logging
from pyrogram import Client, types
from bot.config import Config
from database import db
from aiohttp import web

async def set_commands(app: Client):
    commands = [
        types.BotCommand("start", "Start the bot"),
        types.BotCommand("admin", "Admin commands"),
    ]
    await app.set_bot_commands(commands)


async def get_admins():
    config = await db.config.get_config("ADMINS")
    return config["value"]


async def add_admin(user_id):
    config = await db.config.get_config("ADMINS")
    if config:
        admins = config["value"]
        if user_id not in admins:
            admins.append(user_id)
            await db.config.update_config("ADMINS", admins)
            return True
    else:
        await db.config.add_config("ADMINS", [user_id])
        return True

    return False


async def remove_admin(user_id):
    config = await db.config.get_config("ADMINS")
    if config:
        admins = config["value"]
        if user_id in admins:
            admins.remove(user_id)
            await db.config.update_config("ADMINS", admins)
            return True
    return False


async def start_webserver():
    routes = web.RouteTableDef()

    @routes.get("/", allow_head=True)
    async def root_route_handler(request):
        res = {
            "status": "running",
        }
        return web.json_response(res)

    async def web_server():
        web_app = web.Application(client_max_size=30000000)
        web_app.add_routes(routes)
        return web_app

    app = web.AppRunner(await web_server())
    await app.setup()
    await web.TCPSite(app, "0.0.0.0", 8000).start()
    logging.info("Web server started")


async def set_commands(app):
    COMMANDS = [
        types.BotCommand("start", "Used to start the bot."),
        types.BotCommand("help", "Used to get help."),
        # types.BotCommand("adminhelp", "Used to get admin commands."),
    ]
    await app.set_bot_commands(COMMANDS)


async def add_user(user_id):
    user = await db.users.get_user(user_id)
    if user:
        return
    await db.users.create_user(user_id)
    return True
