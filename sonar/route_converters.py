# Swiss Open Access Repository
# Copyright (C) 2021-2026 RERO
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

"""Werkzeug Route Converters."""

from urllib.parse import urlparse

from flask import current_app, g, request
from werkzeug.routing import BaseConverter, ValidationError

from .modules.organisations.api import OrganisationRecord, OrganisationSearch


class OrganisationCodeConverter(BaseConverter):
    """Werkzeug Organisation code converter."""

    # any word
    regex = r"\w+"

    def to_python(self, value):
        """Check that the value is a known organisation view code.

        :param value: the URL param value.
        :returns: the URL param value.
        """
        if g.get("organisation"):
            g.pop("organisation")
        if value == current_app.config.get("SONAR_APP_DEFAULT_ORGANISATION"):
            # Deny the global view on dedicated portals
            server_name = urlparse(request.url).hostname
            if OrganisationSearch().get_organisation_pid_by_server_name(server_name):
                raise ValidationError
            return value
        organisation = OrganisationRecord.get_record_by_pid(value)
        if not organisation or not organisation.get("isShared"):
            raise ValidationError
        g.organisation = organisation.dumps()
        return value
