# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# My site is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.


"""Institution extension."""

from __future__ import absolute_import, print_function


class Institutions(object):
    """Institution extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions["sonar_institutions"] = self

    def init_config(self, app):
        """Initialize configuration.

        Override configuration variables with the values in this package.
        """
