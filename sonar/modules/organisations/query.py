# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Query for organisations."""

from flask import current_app

from sonar.modules.organisations.api import current_organisation
from sonar.modules.query import default_search_factory
from sonar.modules.users.api import current_user_record


def search_factory(self, search, query_parser=None):
    """Organisation search factory.

    :param search: Search instance.
    :param query_parser: Url arguments.
    :returns: Tuple with search instance and URL arguments.
    """
    search, urlkwargs = default_search_factory(self, search)

    if current_app.config.get("SONAR_APP_DISABLE_PERMISSION_CHECKS"):
        return (search, urlkwargs)

    # Records are not filtered for superusers.
    if current_user_record.is_superuser:
        return (search, urlkwargs)

    # For admins, records are filtered by organisation of the current user.
    search = search.filter("term", code=current_organisation["pid"])

    return (search, urlkwargs)
