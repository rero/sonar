# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# My site is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.


"""Document extension."""

from __future__ import absolute_import, print_function

from . import config


class Documents(object):
    """SONAR documents extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions["sonar_documents"] = self

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith("SONAR_DOCUMENTS_"):
                app.config.setdefault(k, getattr(config, k))
