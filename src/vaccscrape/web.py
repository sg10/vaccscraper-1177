import logging

import cherrypy

from vaccscrape import config, io

logger = logging.getLogger(__name__)


class WebServer:
    @cherrypy.expose("status")
    def status(self):
        TIME_WINDOW_SEC = 60 * 60
        successes = io.read_latest_successes__sync(TIME_WINDOW_SEC)

        msg = f"{len(successes)} successful scrape(s) per hour<br/>"
        if len(successes) < config.MONITOR_SUCCESSES_PER_HOUR:
            msg += "ERROR"
        else:
            msg += "scraping like a rockstar"

        return msg

    @cherrypy.expose
    def index(self):
        bootstrap_css = (
            '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstr'
            'ap@4.6.0/dist/css/bootstrap.min.css" integrity="sha384-B0vP5xmATw'
            '1+K9KRQjQERJvTumQW0nPEzvF6L/Z6nronJ3oUOFUFpCjEUQouq2+l" crossorig'
            'in="anonymous">'
        )

        page = self.scrapes_page()

        content = (
            f'<html>{bootstrap_css}<meta charset="utf-8"/>'
            f'<body style="padding: 2em;">{page}</body></html>'
        )
        return content.encode("utf8")

    def scrapes_page(self):
        TIME_WINDOW_SEC = 24 * 60 * 60

        success_results = io.read_latest_successes__sync(TIME_WINDOW_SEC)
        error_results = io.read_latest_errors__sync(TIME_WINDOW_SEC)

        errors_list = []
        successes_list = []

        for i in range(len(success_results)):
            previous_result = success_results[i - 1] if i >= 0 else []
            result = success_results[i]

            prev = set(previous_result.headlines)
            curr = set(result.headlines)

            diff_headlines = list(curr.difference(prev))

            row = ""
            if len(diff_headlines) > 0 or i == 0:
                row += f"<li><strong>{result.timestamp}:</strong></li>"
                if i > 0:
                    diff_headlines.sort(
                        key=lambda x: previous_result.headlines.index(x)
                        if x in previous_result.headlines
                        else -1
                    )
                else:
                    diff_headlines = result.headlines

                row += "<ul>"
                for h in diff_headlines:
                    row += f"<li>{h}</li>"
                row += "</ul>"
            else:
                row += f"<li><strong>{result.timestamp}</strong>:"
                row += "(no change)</li>"

            successes_list.append(row)

        for i in range(len(error_results)):
            previous_result = error_results[i - 1] if i >= 0 else ""
            result = error_results[i]

            diff = (
                result.error_message
                if result.error_message != previous_result.error_message
                else ""
            )

            if i == 0:
                row = f"<li><strong>{result.timestamp}</strong>:"
                row += "{result.error_message}</li>"
            elif len(diff) > 0:
                row = f"<li><strong>{result.timestamp}: "
                row += "{diff}</strong></li>"
            else:
                row = f"<li><strong>{result.timestamp}</strong>: "
                row += "(same error)</li>"

            errors_list.append(row)

        successes_list.reverse()
        successes_rows = "\n".join(successes_list)

        errors_list.reverse()
        errors_rows = "\n".join(errors_list)

        message = "<h1>1177.se Vaccination Sign-Up Notifier</h1>"
        message += f"<h2>Error</h2>{errors_rows}<h2>Success</h2>{successes_rows}"

        return message


def run_logs_server():
    logger.info("Starting logs server")
    cherrypy.config.update(
        {
            "server.socket_port": config.ALIVE_PAGE_PORT,
            "server.socket_host": config.ALIVE_PAGE_HOST,
        }
    )
    cherrypy.quickstart(WebServer())
