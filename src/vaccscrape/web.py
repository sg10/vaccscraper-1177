import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

from vaccscrape import config, io

logger = logging.getLogger(__name__)


class S(BaseHTTPRequestHandler):
    def _set_headers(self, http_status_code: int = 200):
        self.send_response(http_status_code)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _html(self, message):
        """This just generates an HTML document that includes `message`
        in the body. Override, or re-write this do do more interesting stuff.
        """
        bootstrap_css = (
            '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstr'
            'ap@4.6.0/dist/css/bootstrap.min.css" integrity="sha384-B0vP5xmATw'
            '1+K9KRQjQERJvTumQW0nPEzvF6L/Z6nronJ3oUOFUFpCjEUQouq2+l" crossorig'
            'in="anonymous">'
        )

        content = (
            f'<html>{bootstrap_css}<meta charset="utf-8"/>'
            f'<body style="padding: 2em;">{message}</body></html>'
        )
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        TIME_WINDOW_SEC = 24 * 60 * 60

        success_results = io.read_latest_successes__sync(TIME_WINDOW_SEC)
        error_results = io.read_latest_errors__sync(TIME_WINDOW_SEC)

        # set header for remote status monitoring
        if len(success_results) == 0:
            self._set_headers(500)
        else:
            self._set_headers(200)

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

        message = f"<h1>1177.se Vaccination Sign-Up Notifier</h1>"
        message += f"<h2>Error</h2>{errors_rows}<h2>Success</h2>{successes_rows}"
        self.wfile.write(self._html(message))

    def do_HEAD(self):
        self._set_headers()


def run_logs_server():
    logger.info("Starting logs server")
    server_address = (config.ALIVE_PAGE_HOST, config.ALIVE_PAGE_PORT)
    httpd = HTTPServer(server_address, S)
    httpd.serve_forever()
