import aiohttp
import logging

from .config import Config


logger = logging.getLogger(__name__)


class Bot:
    __instance__ = None

    def __init__(self):
        if Bot.__instance__ is None:
            self.bot_token = Config.BOT_TOKEN
            self.app_name = Config.APP_NAME
            self.api_base_url = f"https://api.telegram.org/bot{self.bot_token}"
            Bot.__instance__ = self
        else:
            raise Exception("You cannot create another SingletonGovt class")

    @staticmethod
    def get_instance():
        if not Bot.__instance__:
            Bot()
        return Bot.__instance__

    async def _req(self, method, url, **kwargs):
        async with aiohttp.ClientSession() as session:
            r = await session.request(method=method, url=url, **kwargs)
            logger.debug(await r.text())
            return r

    async def send_message(self, **kwargs):
        url = self.api_base_url + "/sendMessage"
        await self._req(method="POST", url=url, json=kwargs)

    async def set_webhook(self):
        url = self.api_base_url + "/setWebhook"
        json = {"url": f"https://{self.app_name}.herokuapp.com/{self.bot_token}"}
        await self._req(method="POST", url=url, json=json)

    async def delete_webhook(self):
        url = self.api_base_url + "/deleteWebhook"
        await self._req(method="GET", url=url)
