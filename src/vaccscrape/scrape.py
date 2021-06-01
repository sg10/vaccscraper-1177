import logging
from typing import List

from pyppeteer import launch
from pyppeteer.errors import PyppeteerError

from vaccscrape import config, io
from vaccscrape.models import ScrapeError, ScrapeResult, ScrapeSuccess

logger = logging.getLogger(__name__)


async def scrape() -> List[ScrapeResult]:

    scrape_results = []

    for service_name, scrape_page in config.PAGES.items():

        logger.info(f"Fetching {service_name}")

        browser = await launch(options={"headless": True, "args": ["--no-sandbox"]})
        page = await browser.newPage()

        try:

            await page.goto(scrape_page.url)

            dom_elements = await page.JJ(scrape_page.selector)
            text_elements = [
                await page.evaluate("(element) => element.textContent", e)
                for e in dom_elements
            ]

            result = ScrapeSuccess(headlines=text_elements, service=service_name)
            logger.info("Fetch success")

        except PyppeteerError as error:
            logger.info(error)
            message = str(error)
            if len(message) > 60:
                message = message[:60] + " ..."

            result = ScrapeError(error_message=message, service=service_name)

        await browser.close()

        scrape_results.append(result)

    return scrape_results


async def scrape_and_save() -> None:
    try:
        result = await scrape()
        await io.write_multiple(result)
    except Exception as e:
        error_message = str(e)
        logger.error(error_message)
        result = ScrapeError(error_message=error_message, service="")
        await io.write_single(result)
