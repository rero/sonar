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

SHIBBOLETH_SERVICE_PROVIDER_CERTIFICATE = None
"""Path to the service provider certificate.

Left undefined on purpose: the certificate identifies the service provider to
the identity providers, so it must be registered in the SWITCH edu-ID resource
registry. Each environment provides its own pair, outside of this repository.
SAML authentication stays disabled until both this and the private key are set.
"""

SHIBBOLETH_SERVICE_PROVIDER_PRIVATE_KEY = None
"""Path to the service provider private key."""

SHIBBOLETH_IDENTITY_PROVIDERS_CERTIFICATES_PATH = "./data/idp_certificates"
"""Directory storing the identity providers certificates, named <key>.crt."""

SHIBBOLETH_SERVICE_PROVIDER = {}
"""Configuration of service provider."""

SHIBBOLETH_IDENTITY_PROVIDERS = {}
"""Configuration of identity providers."""

SHIBBOLETH_STATE_EXPIRES = 300
"""Number of seconds after which the state token expires."""
