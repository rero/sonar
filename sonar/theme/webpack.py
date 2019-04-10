# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""JS/CSS Webpack bundles for theme."""

from __future__ import absolute_import, print_function

from flask_webpackext import WebpackBundle

theme = WebpackBundle(
    __name__,
    'assets',
    entry={
        'sonar-theme': './scss/sonar/theme.scss',
    },
    dependencies={
        'bootstrap': '^4.3',
        'font-awesome': '^4.0'
    }
)
