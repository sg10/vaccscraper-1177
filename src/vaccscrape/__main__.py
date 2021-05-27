import asyncio
import logging
import os

from src.vaccscrape.web import run_logs_server
from vaccscrape import config
from vaccscrape.constants import ENV_DEBUG
from vaccscrape.notifier import notifier, send_notification
from vaccscrape.scrape import scrape_and_save

logger = logging.getLogger(__name__)


async def run_scraper(event_scraped: asyncio.Event):
    logger.info("Starting scraper")
    while True:
        try:
            await scrape_and_save()
            event_scraped.set()
            await asyncio.sleep(config.INTERVAL_SCRAPE_SEC)
        except Exception as e:
            logger.error(e)


async def run_notifier(event_scraped: asyncio.Event):
    logger.info("Starting notifier")
    while True:
        try:
            await event_scraped.wait()
            event_scraped.clear()
            await notifier()
        except Exception as ex:
            logger.error(ex)


async def main():
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)

    logger.info("Application started")

    if os.environ.get(ENV_DEBUG):
        logger.info("Debug mode")

    assert os.path.exists(config.PUSHSAFER_CONFIG_FILE)

    event_scraped = asyncio.Event()

    scraper_task = asyncio.create_task(run_scraper(event_scraped))
    examine_task = asyncio.create_task(run_notifier(event_scraped))
    webserver_task = asyncio.create_task(run_logs_server())

    send_notification("Web service started!", important=False)

    await webserver_task
    await scraper_task
    await examine_task


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
