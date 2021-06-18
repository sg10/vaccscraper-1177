import configparser
import os
from enum import Enum
from typing import Dict

from pydantic.dataclasses import dataclass

CONFIG_SERVICE_PREFIX = "service."

DB_FILE = os.environ.get("DB_FILE", "db.json")

INTERVAL_SCRAPE_SEC = 5 * 60
TIME_WINDOW_SEC = 60 * 60

MONITOR_SUCCESSES_PER_HOUR = 3

ALIVE_PAGE_HOST = "0.0.0.0"
ALIVE_PAGE_PORT = 8000

PUSHSAFER_TITLE = "Vaccination Update Stockholm"
PUSHSAFER_ICON_ID = 85
PUSHSAFER_CONFIG_FILE = "config.ini"


class ProcessingType(str, Enum):
    SET = "set"
    SINGLE_REGEX_PAD = "single_regex_pad"


@dataclass
class PageToScrape:
    url: str
    selector: str
    processing_type: ProcessingType
    processing_details: str


def fetch_pages() -> Dict[str, PageToScrape]:
    config = configparser.ConfigParser()
    config.read(PUSHSAFER_CONFIG_FILE)

    pages = {}

    for section in config.sections():
        if section.startswith(CONFIG_SERVICE_PREFIX):
            service_name = section.replace(CONFIG_SERVICE_PREFIX, "")
            p = PageToScrape(
                url=config.get(section, "url"),
                selector=config.get(section, "selector"),
                processing_type=config.get(section, "processing_type"),
                processing_details=config.get(section, "processing_details") or "",
            )
            pages[service_name] = p

    return pages


PAGES = fetch_pages()
