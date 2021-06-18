import logging
from typing import Optional, Tuple

from vaccscrape import config, io
from vaccscrape.pushsafer import send_notification

logger = logging.getLogger(__name__)


_last_error_sent = None


async def examine() -> Optional[Tuple[Optional[str], str]]:
    global _last_error_sent

    logger.info("Examine & notify")

    errors = await io.read_latest_errors(config.TIME_WINDOW_SEC)
    all_successes = await io.read_latest_successes(config.TIME_WINDOW_SEC)

    for service_name in config.PAGES.keys():

        successes = [s for s in all_successes if s.service == service_name]

        if len(successes) > 1:
            ultimate_headlines = set(successes[-1].headlines)

            if len(ultimate_headlines) == 0:
                send_notification(service_name, "Result list empty!", send_to_all=False)
                return

            penultimate_headlines = set(successes[-2].headlines)

            # two or success events: report if diff
            diff_plus = ultimate_headlines.difference(penultimate_headlines)

            if diff_plus:
                diff_str = "; ".join(list(diff_plus))
                send_notification(service_name, diff_str, send_to_all=True)
                return

        elif len(errors) > 0:

            e = service_name, errors[-1].error_message
            if e != _last_error_sent:
                send_notification(
                    service_name, errors[-1].error_message, send_to_all=False
                )
                _last_error_sent = service_name, errors[-1].error_message
                return

    if len(all_successes) == len(errors) == 0:
        send_notification("", "Restarted, no recent events.", send_to_all=False)
        return
