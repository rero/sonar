# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Query."""

from flask import current_app

from sonar.modules.organisations.api import current_organisation
from sonar.modules.query import default_search_factory
from sonar.modules.users.api import current_user_record


def search_factory(self, search, query_parser=None):
    """Search factory.

    :param Search search: Search instance
    :return: Tuple with search instance and URL arguments
    :rtype: tuple
    """
    search, urlkwargs = default_search_factory(self, search)

    if current_app.config.get("SONAR_APP_DISABLE_PERMISSION_CHECKS"):
        return (search, urlkwargs)

    # Records are not filtered for superusers.
    if current_user_record.is_superuser:
        return (search, urlkwargs)

    # For admins, records are filtered by organisation of the current user.
    search = search.filter("term", organisation__pid=current_organisation["pid"])

    return (search, urlkwargs)
