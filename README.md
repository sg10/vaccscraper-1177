# 1177 Covid-Vaccination Status Update Scraper

This is a tool that frequently checks the signup for vaccination phases (age groups) on [1177.se](1177.se)
(Swedish public health care guide) and sends a push notification to defined devices (phones, browsers)
via the service [Pushsafer](https://www.pushsafer.com/).

Not pushed is a `config.ini` file of this structure:
```
[pushsafer]
private_key=
device_group_important=
device_group_status=
```

App-specific config (poll time, ports, etc.) is in `config.py`.

Included is a docker build file, I used [dockerize.io](https://dockerize.io) to host the container.
