# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Query for deposits."""

from elasticsearch_dsl import Q
from flask import current_app

from sonar.modules.organisations.api import current_organisation
from sonar.modules.query import default_search_factory
from sonar.modules.users.api import current_user_record


def search_factory(self, search, query_parser=None):
    """Deposit search factory.

    :param search: Search instance.
    :param query_parser: Url arguments.
    :returns: Tuple with search instance and URL arguments.
    """
    search, urlkwargs = default_search_factory(self, search)

    if current_app.config.get("SONAR_APP_DISABLE_PERMISSION_CHECKS"):
        return (search, urlkwargs)

    user = current_user_record

    # For superusers, records are not filtered.
    if user.is_superuser:
        return (search, urlkwargs)

    # For admin and moderator, only records that belongs to his organisation.
    if user.is_admin or user.is_moderator:
        search = search.filter("term", user__organisation__pid=current_organisation["pid"])

        # For moderators having a subdivision, records are filtered by
        # subdivision or by owned deposits
        if not user.is_admin and user.is_moderator and user.get("subdivision"):
            user = user.replace_refs()
            search = search.filter(
                "bool",
                should=[
                    Q("term", user__subdivision__pid=user["subdivision"]["pid"]),
                    Q("term", user__pid=user["pid"]),
                ],
            )

        return (search, urlkwargs)

    # For user, only records that belongs to him.
    if user.is_submitter:
        search = search.filter("term", user__pid=user["pid"])

    return (search, urlkwargs)
