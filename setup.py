# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""SONAR is a future archive of scholarly publications. It intends to collect, promote and preserve the publications of authors affiliated with Swiss public research institutions"""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()

packages = find_packages()

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('sonar', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='sonar',
    version=version,
    description=__doc__,
    long_description=readme,
    keywords='sonar Invenio',
    license='MIT',
    author='RERO',
    author_email='software@rero.ch',
    url='https://github.com/rero/sonar',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            'sonar = invenio_app.cli:cli',
        ],
        'invenio_base.apps': [
            'sonar_records = sonar.records:SwissOpenAccessRepository',
        ],
        'invenio_base.blueprints': [
            'sonar = sonar.theme.views:blueprint',
            'sonar_records = sonar.records.views:blueprint',
        ],
        'invenio_assets.webpack': [
            'sonar_theme = sonar.theme.webpack:theme',
        ],
        'invenio_config.module': [
            'sonar = sonar.config',
        ],
        'invenio_i18n.translations': [
            'messages = sonar',
        ],
        'invenio_base.api_apps': [
            'sonar = sonar.records:SwissOpenAccessRepository',
         ],
        'invenio_jsonschemas.schemas': [
            'sonar = sonar.records.jsonschemas'
        ],
        'invenio_search.mappings': [
            'records = sonar.records.mappings'
        ],
    },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 3 - Alpha',
    ],
)
