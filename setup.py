#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages

setup(name="transloadit",
      version="1.0.0",
      description="Library for interfacing with Transloadit's API",
      author="Joe Stump",
      author_email="joe@joestump.net",
      url="http://github.com/joestump/python-transloadit",
      packages = find_packages(),
      license = "MIT License",
      install_requires=['requests>=2.0.0,<3.0.0'],
      keywords="transloadit",
      zip_safe = True,
      tests_require=['nose', 'coverage'])
