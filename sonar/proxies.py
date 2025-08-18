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
