#!/usr/bin/env python
"""
Setup script for arsf_tools

This file has been created by ARSF Data Analysis Node and
is licensed under the GPL v3 Licence. A copy of this
licence is available to download with this file.

"""

import glob
from distutils.core import setup

scripts_list = glob.glob('*.py')

setup(
  name='arsf_tools',
  version = '0.1',
  description = 'ARSF Tools',
  url = 'https://arsf-dan.nerc.ac.uk/trac/',
  packages = ['arsf_envi_reader'],
  scripts = scripts_list,
)
