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

"""Shibboleth authenticator configuration.

.. code-block:: python
    SHIBBOLETH_IDENTITY_PROVIDERS = dict(
        idp1=dict(
            # Configuration values for idp1
        ),
        idp2=dict(
            # Configuration values for idp2
        )
    )
"""

SHIBBOLETH_SERVICE_PROVIDER_CERTIFICATE = './docker/nginx/sp.pem'
"""Path to certificate."""

SHIBBOLETH_SERVICE_PROVIDER_PRIVATE_KEY = './docker/nginx/sp.key'
"""Path to certificate private key."""

SHIBBOLETH_SERVICE_PROVIDER = {}
"""Configuration of service provider."""

SHIBBOLETH_IDENTITY_PROVIDERS = {}
"""Configuration of identity providers."""

SHIBBOLETH_STATE_EXPIRES = 300
"""Number of seconds after which the state token expires."""
