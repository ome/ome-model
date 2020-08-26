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

from setuptools import setup


def get_version():
    import xml.etree.ElementTree as ElementTree
    tree = ElementTree.parse('pom.xml')
    ns = {'maven': 'http://maven.apache.org/POM/4.0.0'}
    version = tree.find('maven:version', ns).text
    print(version)
    return version.replace('-SNAPSHOT', '.dev0')


def write_version(version):
    with open('ome_model/__init__.py', 'w') as f:
        f.write('__version__ = "%s"\n' % version)


version = get_version()
write_version(version)
url = "https://github.com/ome/ome-model/"

setup(
    version=get_version(),
    packages=["ome_model"],
    name='ome-model',
    description="Core OME model library (EXPERIMENTAL)",
    long_description="TBD",
    classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
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
    python_requires='>=3',
)
