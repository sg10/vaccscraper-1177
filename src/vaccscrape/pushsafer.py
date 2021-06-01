import configparser
import logging
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from vaccscrape import config
from vaccscrape.constants import ENV_DEBUG

logger = logging.getLogger(__name__)


def send_notification(service_name: str, message: str, important: bool) -> None:
    logger.info(f"Sending push notification for {service_name}")

    page_scrape = config.PAGES.get(service_name)

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

    href_url = page_scrape.url if page_scrape else ""

    if service_name:
        message = service_name + ":" + message

    url = "https://www.pushsafer.com/api"  # Set destination URL here
    post_fields = {  # Set POST fields here
        "t": config.PUSHSAFER_TITLE,
        "m": message,
        # "s": sound,
        # "v": vibration,
        "i": config.PUSHSAFER_ICON_ID,
        # "c": iconcolor,
        "d": device_group,
        "u": href_url,
        "ut": service_name or "General",
        "k": pushsafer_config["pushsafer"]["private_key"],
    }

    try:
        request = Request(url, urlencode(post_fields).encode())
        urlopen(request).read().decode()
        logger.info("Notification sent")
    except Exception as e:
        logger.error(str(e))
