# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2021 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
        service_provider['x509certNew'] = app.config.get(
            'SHIBBOLETH_SERVICE_PROVIDER_NEW_CERTIFICATE')
        service_provider['private_key'] = app.config.get(
            'SHIBBOLETH_SERVICE_PROVIDER_PRIVATE_KEY')

        app.config.setdefault('SHIBBOLETH_SERVICE_PROVIDER', service_provider)

        for k in dir(config):
            if k.startswith('SHIBBOLETH_'):
                app.config.setdefault(k, getattr(config, k))
