# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

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

SHIBBOLETH_SERVICE_PROVIDER_CERTIFICATE = "./docker/nginx/sp.pem"
"""Path to certificate."""

SHIBBOLETH_SERVICE_PROVIDER_PRIVATE_KEY = "./docker/nginx/sp.key"
"""Path to certificate private key."""

SHIBBOLETH_SERVICE_PROVIDER = {}
"""Configuration of service provider."""

SHIBBOLETH_IDENTITY_PROVIDERS = {}
"""Configuration of identity providers."""

SHIBBOLETH_STATE_EXPIRES = 300
"""Number of seconds after which the state token expires."""
