# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

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
