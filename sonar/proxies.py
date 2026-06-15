# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Helper proxies to the state object."""

from flask import current_app
from werkzeug.local import LocalProxy


class SonarProxy:
    """SONAR proxy class."""

    extension = None

    def __init__(self):
        """Proxy initialization."""
        self.extension = current_app.extensions["sonar"]

    @property
    def resources(self):
        """Get the registered resources.

        :returns: Dictionary of registered resources.
        """
        return self.extension.resources

    @property
    def endpoints(self):
        """Get the list of endpoints.

        :returns: Dictionary of registered endpoints.
        """
        return self.extension.get_endpoints()

    def service(self, resource_type):
        """Return the service corresponding to resource.

        :param resource_type: Type of resource.
        :returns: A service instance
        """
        if not self.resources.get(resource_type):
            return None

        return self.resources[resource_type].service


sonar = LocalProxy(SonarProxy)
"""Proxy to the SONAR extension."""
