import asyncio
import logging
import re
from typing import List

from pyppeteer import launch
from pyppeteer.errors import PyppeteerError

from vaccscrape import config, io
from vaccscrape.config import ProcessingType
from vaccscrape.models import ScrapeError, ScrapeResult, ScrapeSuccess

logger = logging.getLogger(__name__)


async def scrape() -> List[ScrapeResult]:

    scrape_results = []

    browser = await launch(options={"headless": True, "args": ["--no-sandbox"]})

    for service_name, scrape_page in config.PAGES.items():

        logger.info(f"Fetching {service_name}")
        page = await browser.newPage()

        try:

            await page.goto(scrape_page.url)
            await page.waitFor(scrape_page.selector)
            dom_elements = await page.JJ(scrape_page.selector)
            text_elements = [
                await page.evaluate("(element) => element.textContent", e)
                for e in dom_elements
            ]

            if scrape_page.processing_type == ProcessingType.SINGLE_REGEX_PAD:
                merged = "".join(text_elements)
                matched = re.findall(scrape_page.processing_details, merged)
                matched = [f"...{m}..." for m in matched]
                result = ScrapeSuccess(headlines=matched, service=service_name)

            elif scrape_page.processing_type == ProcessingType.SET:
                result = ScrapeSuccess(headlines=text_elements, service=service_name)

            else:
                raise RuntimeError(
                    f"Unknown processing type: {scrape_page.processing_type}"
                )

            logger.info("Fetch success")

        except PyppeteerError as error:
            logger.info(error)
            message = str(error)
            if len(message) > 60:
                message = message[:60] + " ..."

            result = ScrapeError(error_message=message, service=service_name)

        await page.close()

        scrape_results.append(result)

    await browser.close()

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
