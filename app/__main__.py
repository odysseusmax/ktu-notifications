import logging

from aiohttp import web

from .config import Config
from .main import app


logging.basicConfig(level=logging.DEBUG if Config.DEBUG else logging.INFO)
logging.getLogger("aiohttp").setLevel(logging.INFO if Config.DEBUG else logging.WARNING)


web.run_app(app, host=Config.HOST, port=Config.PORT)
