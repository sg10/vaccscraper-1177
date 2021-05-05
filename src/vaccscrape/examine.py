import logging
from typing import Optional

from vaccscrape import io
from vaccscrape import config

logger = logging.getLogger(__name__)


_last_error_sent = None


async def examine() -> Optional[str]:
    global _last_error_sent

    logger.info("Examine")

    errors = await io.read_latest_errors(config.TIME_WINDOW_SEC)
    successes = await io.read_latest_successes(config.TIME_WINDOW_SEC)

    if len(successes) > 1:
        ultimate_headlines = set(successes[-1].headlines)
        penultimate_headlines = set(successes[-2].headlines)

        # two or success events: report if diff
        diff_plus = ultimate_headlines.difference(penultimate_headlines)

        if diff_plus:
            return "; ".join(list(diff_plus))
        else:
            return None

    elif len(errors) > 0:

        e = errors[-1].error_message
        if e != _last_error_sent:
            _last_error_sent = e
            return e
        else:
            return None

    elif len(successes) == len(errors) == 0:

        return "Restarted, no recent events."

    return None
