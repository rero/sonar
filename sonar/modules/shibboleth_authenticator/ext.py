# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Shibboleth authenticator extension."""

from . import config


class ShibbolethAuthenticator:
    """Shibboleth authenticator extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions["shibboleth_authenticator"] = self

    def init_config(self, app):
        """Initialize configuration."""
        # Update service provider configuration with the configured certificate
        # paths. They are only injected when set, so that an unconfigured
        # instance raises the explicit error from ``init_saml_auth`` instead of
        # trying to open ``None``.
        service_provider = app.config.get("SHIBBOLETH_SERVICE_PROVIDER")
        certificate = app.config.get("SHIBBOLETH_SERVICE_PROVIDER_CERTIFICATE")
        private_key = app.config.get("SHIBBOLETH_SERVICE_PROVIDER_PRIVATE_KEY")

        if certificate:
            service_provider["x509cert"] = certificate

        if private_key:
            service_provider["private_key"] = private_key

        app.config.setdefault("SHIBBOLETH_SERVICE_PROVIDER", service_provider)

        for k in dir(config):
            if k.startswith("SHIBBOLETH_"):
                app.config.setdefault(k, getattr(config, k))
