import json
import logging

from aiohttp import web

from .config import Config
from .bot import Bot


routes = web.RouteTableDef()
logger = logging.getLogger(__name__)


@routes.get("/")
async def home(request):
    return web.Response(text="Hi There!")


@routes.get("/api")
async def api(request):
    n = []
    if Config.NOTIFICATIONS_FILE.exists():
        n = json.load(open(Config.NOTIFICATIONS_FILE, "r"))
    if request.query.get("pretty", "0") == "1":
        return web.Response(text=json.dumps(n, indent=4))
    return web.json_response(n)


@routes.post("/{token}")
async def handle_tg(request):
    bot = Bot.get_instance()
    update = await request.json()
    logger.debug("input from telegram %s", update)
    message = update.get("message")
    if message:
        await bot.send_message(
            chat_id=message["chat"]["id"],
            text="Hi there.\n\nJoin @KtuNoticeBoard to get immediate updates from KTU.",
            reply_markup=dict(
                inline_keyboard=[
                    [
                        dict(text="Join Channel!", url="https://t.me/KtuNoticeBoard"),
                        dict(text="View on web!", url="https://tx.me/s/KtuNoticeBoard"),
                    ],
                    [
                        dict(
                            text="This is a part of @odbots.", url="https://t.me/odbots"
                        )
                    ],
                ]
            ),
            reply_to_message_id=message["message_id"],
        )
    return web.Response(text="OK")
