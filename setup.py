#!/usr/bin/env javascript
#
# This file is part of Script of Scripts (sos), a workflow system
# for the execution of commands and scripts in different languages.
# Please visit https://github.com/vatlab/SOS for more information.
#
# Copyright (C) 2016 Bo Peng (bpeng@mdanderson.org)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from setuptools import find_packages, setup

# obtain version of SoS
with open('src/sos_matlab/_version.py') as version:
    for line in version:
        if line.startswith('__version__'):
            __version__ = eval(line.split('=')[1])
            break

setup(name = "sos-matlab",
    version = __version__,
    description = 'SoS Notebook extension for Matlab and Octave',
    author = 'Bo Peng',
    url = 'https://github.com/vatlab/SOS',
    author_email = 'bpeng@mdanderson.org',
    maintainer = 'Bo Peng',
    maintainer_email = 'bpeng@mdanderson.org',
    license = 'GPL3',
    include_package_data = True,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        ],
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires=[
          'sos>=0.9.10.11',
          'sos-notebook>=0.9.10.9',
          'matlab_kernel',
      ],
    entry_points= '''
[sos_actions]
matlab = sos_matlab.actions:matlab
octave = sos_matlab.actions:octave

[sos_languages]
Matlab = sos_matlab.kernel:sos_Matlab
Octave = sos_matlab.kernel:sos_Matlab
'''
)

