# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# My site is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Shibboleth authenticator extension."""

from __future__ import absolute_import, print_function

from . import config


class ShibbolethAuthenticator(object):
    """Shibboleth authenticator extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['shibboleth_authenticator'] = self

    def init_config(self, app):
        """Initialize configuration."""
        # Update service provider configuration with certificate path found
        # in environment variables
        service_provider = app.config.get('SHIBBOLETH_SERVICE_PROVIDER')
        service_provider['x509cert'] = app.config.get(
            'SHIBBOLETH_SERVICE_PROVIDER_CERTIFICATE')
        service_provider['private_key'] = app.config.get(
            'SHIBBOLETH_SERVICE_PROVIDER_PRIVATE_KEY')

        app.config.setdefault('SHIBBOLETH_SERVICE_PROVIDER', service_provider)

        for k in dir(config):
            if k.startswith('SHIBBOLETH_'):
                app.config.setdefault(k, getattr(config, k))
