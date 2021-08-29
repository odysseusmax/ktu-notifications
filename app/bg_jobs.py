import json
import asyncio
import datetime
import logging

import yarl
import motor.motor_asyncio

from .notifications import fetch_notifications
from .bot import Bot
from .config import Config


logger = logging.getLogger(__name__)


def find_difference(a, b):
    b_text = []
    for i in b:
        b_text.append(i["text"])
    return [item for item in a if item["text"] not in b_text]


async def initiate_notify(notification):
    bot = Bot.get_instance()
    chnl = Config.PUBLISH_CHANNEL_ID
    for i in notification:
        if not i:
            continue

        logger.debug(i)
        whatsapp_share_link = generate_whatsapp_share_link(i["text"])
        await bot.send_message(
            chat_id=chnl,
            text=i["formatted"],
            reply_markup=dict(
                inline_keyboard=[
                    [dict(text="Share To WhatsApp!", url=whatsapp_share_link)]
                ]
            ),
            parse_mode="HTML",
        )
        await asyncio.sleep(3)
        await bot.send_message(
            chat_id=Config.ADMIN_ID, text=i["formatted"], parse_mode="HTML"
        )
        await asyncio.sleep(3)


def generate_whatsapp_share_link(text):
    query = {
        "text": f"{text}\n\nGet Instant KTU Updates at https://t.me/KtuNoticeBoard or https://tx.me/s/KtuNoticeBoard"
    }
    return str(
        yarl.URL.build(
            scheme="https", host="api.whatsapp.com", path="/send", query=query
        )
    )


async def notification_fetcher():
    try:
        bot = Bot.get_instance()
        client = motor.motor_asyncio.AsyncIOMotorClient(Config.DATABASE_URL)
        db = client.notifications
        collection = db.notifications
        existing_notifications = await collection.find_one({"notification": True})
        cur_notifications = json.loads(existing_notifications["data"])
        with open(Config.NOTIFICATIONS_FILE, "w") as fp:
            json.dump(cur_notifications, fp)

        while True:
            try:
                notifications = await fetch_notifications()
                if isinstance(notifications, str):
                    await bot.send_message(chat_id=Config.ADMIN_ID, text=notifications)
                    x = 1
                else:
                    change = find_difference(notifications, cur_notifications)
                    if change:
                        with open(Config.NOTIFICATIONS_FILE, "w") as fp:
                            json.dump(notifications, fp)

                        await collection.update_one(
                            {"notification": True},
                            {
                                "$set": {
                                    "data": json.dumps(notifications),
                                    "updated_at": datetime.datetime.utcnow().isoformat(),
                                }
                            },
                        )
                        # await initiate_notify(change)
                        logger.info("potential new notification detected!")
                        cur_notifications = notifications

                    logger.info("one more done, many to go!")
                    x = 2
                await asyncio.sleep(60 * x)
            except Exception as e:
                logger.error(e, exc_info=True)
        logger.info("Stopped notification fetching")
    except Exception as e:
        logger.error(e, exc_info=True)
