#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages

setup(name="transloadit",
      version="0.0.5",
      description="Library for interfacing with Transloadit's API",
      author="Joe Stump",
      author_email="joe@joestump.net",
      url="http://github.com/joestump/python-transloadit",
      packages = find_packages(),
      license = "MIT License",
      keywords="transloadit",
      zip_safe = True,
      tests_require=['nose', 'coverage'])
