# Copyright 2018 Seth Michael Larson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
from setuptools import setup, find_packages


# Parsing the __about__.py file for dunders
base_dir = os.path.dirname(os.path.abspath(__file__))
about_regex = re.compile(r'^__([^_]+)__\s+=\s+[\'\"]([^\'\"]+)[\'\"]$')
about = {}
with open(os.path.join(base_dir, 'armonaut', '__about__.py'), 'r') as f:
    for line in f:
        match = about_regex.match(line.strip())
        if match:
            about[match.group(1)] = match.group(2)


# Call setup() with our parsed information
setup(
    name=about['title'],
    version=about['version'],
    license=about['license'],
    packages=find_packages('.', exclude=['tests', '.tox']),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing'
    ]
)
