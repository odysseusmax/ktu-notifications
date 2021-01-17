import os
from pathlib import Path


class Config:
    NOTIFICATIONS_FILE = Path("notifications.json")

    PORT = os.environ.get("PORT", "3141")
    HOST = os.environ.get("HOST", "0.0.0.0")

    DEBUG = bool(os.environ.get("DEBUG"))

    BOT_TOKEN = os.environ["BOT_TOKEN"]
    APP_NAME = os.environ["APP_NAME"]
    PUBLISH_CHANNEL_ID = int(os.environ["PUBLISH_CHANNEL_ID"])
    ADMIN_ID = int(os.environ["ADMIN_ID"])

    DATABASE_URL = os.environ["DATABASE_URL"]
