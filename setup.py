#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_packages

setup(
    name="vaccscrape",
    version="1.0",
    description="1177.se covid-19 vaccine information notifier",
    author="Stefan Gruber",
    author_email="mail@stefangruber.net",
    url="https://www.github.com/sg10/vacc-scrape",
    packages=find_packages("src"),
    package_dir={"": "src/"},
)
