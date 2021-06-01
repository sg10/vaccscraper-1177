import datetime
from typing import List

import pydantic
from tinydb import Query, TinyDB

from vaccscrape import config
from vaccscrape.models import ScrapeError, ScrapeResult, ScrapeSuccess


def _get_db() -> TinyDB:
    return TinyDB(config.DB_FILE)


async def write_single(result: ScrapeResult) -> None:
    db = _get_db()
    db.insert(result.dict())
    db.close()


async def write_multiple(results: List[ScrapeResult]) -> None:
    db = _get_db()
    for result in results:
        db.insert(result.dict())
    db.close()


async def read_latest_successes(seconds: int) -> List[ScrapeSuccess]:
    return _read_latest("SCRAPE_SUCCESS", seconds)


async def read_latest_errors(seconds: int) -> List[ScrapeError]:
    return _read_latest("SCRAPE_ERROR", seconds)


def read_latest_successes__sync(seconds: int) -> List[ScrapeSuccess]:
    return _read_latest("SCRAPE_SUCCESS", seconds)


def read_latest_errors__sync(seconds: int) -> List[ScrapeError]:
    return _read_latest("SCRAPE_ERROR", seconds)


def _read_latest(kind: str, seconds: int):
    db = _get_db()
    q = Query()
    start = datetime.datetime.now() - datetime.timedelta(seconds=seconds)
    res = db.search((q.kind == kind) & (q.timestamp > start.isoformat()))
    db.close()
    return [pydantic.parse_obj_as(ScrapeResult, o) for o in res]
