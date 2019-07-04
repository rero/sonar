# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

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
