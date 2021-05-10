# 1177 Covid-Vaccination Status Update Scraper

This is a tool that frequently checks the signup for vaccination phases (age groups) on [1177.se](http://www.1177.se)
(Swedish public health care guide) and sends a push notification to defined devices (phones, browsers)
via the service [Pushsafer](https://www.pushsafer.com/).

### Config
Not included in this repo is a `config.ini` file of this structure:
```
[pushsafer]
private_key=
device_group_important=
device_group_status=
```

App-specific config (poll time, ports, etc.) is in `config.py`.

### Hosting

Included is a docker build file, used [dockerize.io](https://dockerize.io) to host the container. Felt a bit shady.
