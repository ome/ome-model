#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 University of Dundee.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
import os
import sys

from setuptools import setup


version = '6.0.0a3'
url = "https://github.com/ome/ome-model/"

setup(
    version=version,
    packages=["ome_model"],
    name='ome-model',
    description="Core OME model library (EXPERIMENTAL)",
    long_description="TBD",
    classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v2 '
          'or later (GPLv2+)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],  # Get strings from
          # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    author='The Open Microscopy Team',
    author_email='ome-devel@lists.openmicroscopy.org.uk',
    license='GPL-2.0+',
    url='%s' % url,
    zip_safe=False,
    download_url='%s/v%s.tar.gz' % (url, version),
    keywords=['OME', 'Model'],
)
