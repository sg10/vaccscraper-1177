import logging
from typing import Optional, Tuple

from vaccscrape import config, io

logger = logging.getLogger(__name__)


_last_error_sent = None


async def examine() -> Optional[Tuple[Optional[str], str]]:
    global _last_error_sent

    logger.info("Examine")

    errors = await io.read_latest_errors(config.TIME_WINDOW_SEC)
    all_successes = await io.read_latest_successes(config.TIME_WINDOW_SEC)

    for service_name in config.PAGES.keys():

        successes = [s for s in all_successes if s.service == service_name]

        if len(successes) > 1:
            ultimate_headlines = set(successes[-1].headlines)
            penultimate_headlines = set(successes[-2].headlines)

            # two or success events: report if diff
            diff_plus = ultimate_headlines.difference(penultimate_headlines)

            if diff_plus:
                return service_name, "; ".join(list(diff_plus))

        elif len(errors) > 0:

            e = errors[-1].error_message
            if e != _last_error_sent:
                _last_error_sent = e
                return service_name, e

    if len(all_successes) == len(errors) == 0:
        return None, "Restarted, no recent events."

    return None
