import asyncio

from aiohttp import web

from .routes import routes
from .bot import Bot
from .bg_jobs import notification_fetcher


async def start_background_tasks(app):
    bot = Bot.get_instance()
    await bot.set_webhook()
    app["task"] = asyncio.create_task(notification_fetcher())


async def cleanup_background_tasks(app):
    app["task"].cancel()
    await app["task"]


app = web.Application()
app.add_routes(routes)
app.on_startup.append(start_background_tasks)
app.on_cleanup.append(cleanup_background_tasks)

if __name__ == "__main__":
    web.run_app(app)
