import logging
import uuid
from collections import Counter, defaultdict
from typing import List, Dict

from sanic import Sanic, response

from vaccscrape import config, io
from vaccscrape.models import ScrapeError, ScrapeSuccess

logger = logging.getLogger(__name__)

app = Sanic("Vaccination scraper status page")


@app.route("/status")
async def test(request):
    TIME_WINDOW_SEC = 60 * 60
    all_successes = io.read_latest_successes__sync(TIME_WINDOW_SEC)

    successes = Counter(map(lambda r: r.service, all_successes))

    msg = ""

    for service_name in config.PAGES.keys():
        msg += f"\n{service_name}: "

        num = successes.get(service_name, 0)

        if num >= config.MONITOR_SUCCESSES_PER_HOUR:
            msg += f"SUCCESS "
        else:
            msg += f"ERROR "

        msg += f"- {num} scrape successes within the last hour"

        msg += "<br />\n"

    return response.html(body=msg)


@app.route("/")
async def index(request):
    bootstrap_css = (
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstr'
        'ap@4.6.0/dist/css/bootstrap.min.css" integrity="sha384-B0vP5xmATw'
        '1+K9KRQjQERJvTumQW0nPEzvF6L/Z6nronJ3oUOFUFpCjEUQouq2+l" crossorig'
        'in="anonymous">'
    )

    google_charts_js = '<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>'

    html_head = bootstrap_css + google_charts_js

    page = scrapes_page()

    content = (
        f'{html_head}<meta charset="utf-8"/>'
        f'<div style="padding: 2em;">{page}{histogram("x label", "y label", {"a": 2, "b": 3})}</div>'
    )
    return response.html(body=content)


def histogram(x_label: str, y_label: str, hist_values: Dict[str, int]) -> str:
    div_id = str(uuid.uuid4())

    hist_js = ", ".join([f'["{k}", {v}]' for k, v in hist_values.items()])

    return (
        '<script type="text/javascript">'
        '  google.charts.load("current", {packages:["corechart"]});'
        "  google.charts.setOnLoadCallback(drawChart);"
        "  function drawChart() {"
        "    var data = google.visualization.arrayToDataTable(["
        f'     ["{x_label}", "{y_label}"],'
        f"      {hist_js}"
        "]);"
        "    var options = {"
        '      title: "Lengths of dinosaurs, in meters",'
        '      legend: { position: "none" },'
        "    };"
        f'    var chart = new google.visualization.Histogram(document.getElementById("{div_id}"));'
        "    chart.draw(data, options);"
        "  }"
        "</script>"
        f'<div id="{div_id}" style="width: 900px; height: 500px;"></div>'
    )


def scrapes_page():
    TIME_WINDOW_SEC = 24 * 60 * 60

    success_results = defaultdict(list)
    for s in io.read_latest_successes__sync(TIME_WINDOW_SEC):
        success_results[s.service].append(s)

    error_results = defaultdict(list)
    for s in io.read_latest_errors__sync(TIME_WINDOW_SEC):
        error_results[s.service].append(s)

    message = "<h1>Vaccination Sign-Up Notifier</h1>" + '<div class="row">'

    for service_name in config.PAGES.keys():
        message += (
            '<div class="col">'
            + f"<h2>{service_name}</h2>"
            + section_for_service(
                error_results.get(service_name, []),
                success_results.get(service_name, []),
            )
            + "</div>"
        )

    message += "</div>"

    return message


def section_for_service(
    error_results: List[ScrapeError], success_results: List[ScrapeSuccess]
):
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

    message = ""

    if errors_rows:
        message += f"<h3>Error</h3>{errors_rows}"
    if successes_rows:
        message += f"<h3>Success</h3>{successes_rows}"
    return f"{message}"


def run_logs_server():
    logger.info("Starting logs and monitoring server")

    return app.create_server(
        config.ALIVE_PAGE_HOST, config.ALIVE_PAGE_PORT, return_asyncio_server=True
    )
