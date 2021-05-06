FROM python:3.8-slim-buster

WORKDIR /app

# necessary for chromium
RUN apt-get update -y -q
RUN apt-get install -y -q gconf-service libasound2 libatk1.0-0 libatk-bridge2.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget libcairo-gobject2 libxinerama1 libgtk2.0-0 libpangoft2-1.0-0 libthai0 libpixman-1-0 libxcb-render0 libharfbuzz0b libdatrie1 libgraphite2-3 libgbm1

RUN pip3 install --upgrade pip

COPY requirements.txt requirements.txt
COPY src/ src/
COPY setup.py setup.py
COPY config.ini config.ini

RUN pip3 install . -r requirements.txt

RUN python3 -c 'from pyppeteer import command; command.install()'

ENV DISPLAY=:99

CMD [ "python3", "-m" , "vaccscrape"]