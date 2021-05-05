import logging

from pyppeteer import launch
from pyppeteer.errors import PyppeteerError

from vaccscrape import config, io
from vaccscrape.models import ScrapeError, ScrapeResult, ScrapeSuccess

logger = logging.getLogger(__name__)


async def scrape() -> ScrapeResult:
    logger.info("Fetching page")
    browser = await launch(options={"headless": True, "args": ["--no-sandbox"]})
    page = await browser.newPage()

    try:

        await page.goto(config.PAGE_1_URL)

        elements = await page.JJ(config.HEADING_SELECTOR)
        headlines = [
            await page.evaluate("(element) => element.textContent", e) for e in elements
        ]

        result = ScrapeSuccess(headlines=set(headlines))
        logger.info("Fetch success")

    except PyppeteerError as error:
        logger.info(error)
        message = str(error)
        if len(message) > 60:
            message = message[:60] + " ..."

        result = ScrapeError(error_message=message)

    await browser.close()

    return result


async def scrape_and_save() -> None:
    try:
        result = await scrape()
        await io.write_single(result)
    except Exception as e:
        error_message = str(e)
        logger.error(error_message)
        result = ScrapeError(error_message=error_message)

        await io.write_single(result)
