# Covid-Vaccination Status Update Scraper

This is a tool that frequently checks the signup for vaccination phases (age groups) on [1177.se](http://www.1177.se)
(Swedish public health care guide), [kry.se](https://kry.se/) and [doktor24.se](https://doktor24.se/) (private health 
care services) and sends a push notification to defined devices (phones, browsers)
via the service [Pushsafer](https://www.pushsafer.com/).

### Config
Not included in this repo is a `config.ini` file of this structure:
```
[pushsafer]
private_key=
device_group_important=
device_group_status=

[service.1177]
url=https://www.1177.se/Stockholm/sjukdomar--besvar/lungor-och-luftvagar/inflammation-och-infektion-ilungor-och-luftror/om-covid-19--coronavirus/om-vaccin-mot-covid-19/boka-tid-for-vaccination-mot-covid-19-i-stockholms-lan/
selector=.c-teaser__heading__link
processing_type=set

[service.kry]
url=https://www.kry.se/vaccination/covid-19-vaccin-stockholm/
selector=.css-t0y6vo
processing_type=set

[service.doktor24]
url=https://doktor24.se/vaccin/covid-vaccin/region-stockholm/
selector=h2#reservlista-covid-19
processing_type=set
```

App-specific config (poll time, ports, etc.) is in `config.py`.

### Hosting

Included is a docker build file, used [dockerize.io](https://dockerize.io) to host the container. Felt a bit shady.
