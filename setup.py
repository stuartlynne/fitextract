# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('fitextract/fitextract.py').read(),
    re.M
    ).group(1)


with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")

setup(
    name = "fitextract",
    packages = ["fitextract",],
    install_requires = [ "fit_tool", ],
    entry_points = {
        "console_scripts": ['fitextract = fitextract.fitextract:main']
        },
    version = version,
    description='fitextract parses Garmin FIT files and extracts fields to CSV files',
    long_description = long_descr,
    author = "Stuart Lynne",
    author_email = "stuart.lynne@gmail.com",
    url='http://github.com/stuartlynne/fitextract',
    download_url='http://github.com/stuartlynne/fitextract.git',
    license='MIT',
    keywords=['FIT', 'python_fit_tool'],
    )
