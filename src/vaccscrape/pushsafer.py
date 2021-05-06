import configparser
import logging
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from vaccscrape import config
from vaccscrape.constants import ENV_DEBUG

logger = logging.getLogger(__name__)


def send_notification(message: str, important: bool) -> None:
    logger.info("Sending push notification")

    if os.environ.get(ENV_DEBUG):
        logger.info("Not sending notification, debug mode")
        logger.info(f"   {message} (important={important})")
        return

    pushsafer_config = configparser.ConfigParser()
    pushsafer_config.read(config.PUSHSAFER_CONFIG_FILE)

    if important:
        device_group = pushsafer_config["pushsafer"]["device_group_important"]
    else:
        device_group = pushsafer_config["pushsafer"]["device_group_status"]

    url = "https://www.pushsafer.com/api"  # Set destination URL here
    post_fields = {  # Set POST fields here
        "t": config.PUSHSAFER_TITLE,
        "m": message,
        # "s": sound,
        # "v": vibration,
        "i": config.PUSHSAFER_ICON_ID,
        # "c": iconcolor,
        "d": device_group,
        "u": config.PAGE_1_URL,
        "ut": config.PUSHSAFER_URL_TITLE,
        "k": pushsafer_config["pushsafer"]["private_key"],
    }

    try:
        request = Request(url, urlencode(post_fields).encode())
        urlopen(request).read().decode()
        logger.info("Notification sent")
    except Exception as e:
        logger.error(str(e))


if __name__ == "__main__":
    send_notification("jezus christ this is a test message", important=False)
