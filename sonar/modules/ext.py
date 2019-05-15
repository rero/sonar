# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# My site is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.


"""SONAR modules extension."""

from __future__ import absolute_import, print_function

from . import config


class Sonar(object):
    """Sonar extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['sonar'] = self

    def init_config(self, app):
        """Initialize configuration."""
        # Use theme's base template if theme is installed
        print('asdf')
        for k in dir(config):
            if k.startswith('SONAR_'):
                app.config.setdefault(k, getattr(config, k))
