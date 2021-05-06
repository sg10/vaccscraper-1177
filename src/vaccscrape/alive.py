import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import List

from vaccscrape import config, io
from vaccscrape.models import ScrapeError, ScrapeResult, ScrapeSuccess

logger = logging.getLogger(__name__)


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _html(self, message):
        """This just generates an HTML document that includes `message`
        in the body. Override, or re-write this do do more interesting stuff.
        """
        bootstrap_css = (
            '<link rel="stylesheet" '
            'href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css" '
            'integrity="sha384-B0vP5xmATw1+K9KRQjQERJvTumQW0nPEzvF6L/Z6nronJ3oUOFUFpCjEUQouq2+l" '
            'crossorigin="anonymous">'
        )

        content = f'<html>{bootstrap_css}<meta charset="utf-8"/><body style="padding: 2em;">{message}</body></html>'
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        TIME_WINDOW_SEC = 24 * 60 * 60

        self._set_headers()
        successes = io.read_latest_successes__sync(TIME_WINDOW_SEC)
        for i, r in enumerate(successes[1:], 1):
            r.headlines = set(r.headlines).difference(set(successes[i].headlines))

        errors = io.read_latest_errors__sync(TIME_WINDOW_SEC)
        successes.reverse()
        errors.reverse()

        message = f"<h1>1177.se Vaccination Sign-Up Notifier</h1><h2>Error</h2>{self._list_to_ol(errors)}<h2>Success</h2>{self._list_to_ol(successes)}"
        self.wfile.write(self._html(message))

    def do_HEAD(self):
        self._set_headers()

    def _list_to_ol(self, l: List[ScrapeResult]):
        s = []
        for r in l:
            if isinstance(r, ScrapeSuccess):
                if len(r.headlines) == 0:
                    sublist = "(no change)"
                else:
                    sublist = (
                        f"<ul>{''.join([f'<li>{h}</li>' for h in r.headlines])}</ul>"
                    )
                s.append(f"<li><strong>{r.timestamp}</strong>:  " f"{sublist}</li>")
            elif isinstance(r, ScrapeError):
                s.append(
                    "<li><strong>"
                    + r.timestamp
                    + "</strong>:  "
                    + r.error_message
                    + "</li>"
                )

        return f"<ul>{''.join(s)}</ul>"


def run_logs_server():
    logger.info("Starting logs server")
    server_address = (config.ALIVE_PAGE_HOST, config.ALIVE_PAGE_PORT)
    httpd = HTTPServer(server_address, S)
    httpd.serve_forever()
