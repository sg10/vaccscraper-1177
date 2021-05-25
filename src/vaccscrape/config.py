import os

PAGE_1_URL = "https://www.1177.se/Stockholm/sjukdomar--besvar/lungor-och-luftvagar/inflammation-och-infektion-ilungor-och-luftror/om-covid-19--coronavirus/om-vaccin-mot-covid-19/boka-tid-for-vaccination-mot-covid-19-i-stockholms-lan/"

HEADING_SELECTOR = ".c-teaser__heading__link"

DB_FILE = os.environ.get("DB_FILE", "db.json")

INTERVAL_SCRAPE_SEC = 5 * 60
TIME_WINDOW_SEC = 60 * 60

MONITOR_SUCCESSES_PER_HOUR = 3

ALIVE_PAGE_HOST = "0.0.0.0"
ALIVE_PAGE_PORT = 8000

PUSHSAFER_TITLE = "Vaccination Update Stockholm"
PUSHSAFER_URL_TITLE = "1177.se"
PUSHSAFER_ICON_ID = 85
PUSHSAFER_CONFIG_FILE = "config.ini"
