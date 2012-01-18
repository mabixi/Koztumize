#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Public Domain
from setuptools import setup, find_packages


setup(
    name="Koztumize",
    packages=find_packages(),
    install_requires=[
        "CSStyle", "Flask-SQLAlchemy", "docutils", "CairoSVG",
        "psycopg2", "WeasyPrint", "Brigit"])
