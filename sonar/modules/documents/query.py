# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Query for documents."""

from elasticsearch_dsl.query import Q
from flask import current_app, request

from sonar.modules.organisations.api import current_organisation
from sonar.modules.query import default_search_factory, get_operator_and_query_type
from sonar.modules.users.api import current_user_record
from sonar.modules.utils import get_current_ip


def documents_query_parser(qstr=None):
    """Custom query parser for documents."""
    if not qstr:
        return Q()
    fields = current_app.config.get("SONAR_DOCUMENT_QUERY_BOOSTING", ["*"]).copy()

    # The fulltext field is searched only when the `fulltext` query argument is
    # enabled; otherwise it is removed from the searched fields.
    if request.args.get("fulltext", None) in [None, "0", "false", 0, False]:
        fields = [field for field in fields if not field.startswith("fulltext")]

    operator, query_type = get_operator_and_query_type(qstr)

    return Q(query_type, query=qstr, default_operator=operator, fields=fields, lenient=True)
    # lenient property is necessary to make it wildcards working, see
    # https://github.com/elastic/elasticsearch/issues/39577#issuecomment-468751713
    # for more details.


def search_factory(self, search, query_parser=None):
    """Documents search factory.

    :param search: Search instance.
    :param query_parser: Url arguments.
    :returns: Tuple with search instance and URL arguments.
    """
    search, urlkwargs = default_search_factory(self, search, documents_query_parser)

    if current_app.config.get("SONAR_APP_DISABLE_PERMISSION_CHECKS"):
        return (search, urlkwargs)

    view = request.args.get("view")
    is_privileged = current_user_record and current_user_record.is_moderator

    # Public search: anonymous or non-moderator users, with or without a view.
    if not is_privileged:
        # Don't display masked records
        search = search.filter(
            "bool",
            should=[
                {"bool": {"must_not": [{"exists": {"field": "masked"}}]}},
                {"bool": {"filter": [{"term": {"masked": "not_masked"}}]}},
                {
                    "bool": {
                        "must": [
                            {"term": {"masked": "masked_for_external_ips"}},
                            {"term": {"organisation.ips": get_current_ip()}},
                        ]
                    }
                },
            ],
        )

        # Filter record by organisation view. No view means the global scope
        # (all organisations).
        if view and view != current_app.config.get("SONAR_APP_DEFAULT_ORGANISATION"):
            search = search.filter("term", organisation__pid=view)

        # Filter collection
        if request.args.get("collection_view"):
            search = search.filter("term", collections__pid=request.args["collection_view"])
    # Moderator/admin
    else:
        if view:
            # Filter record by organisation view.
            if view != current_app.config.get("SONAR_APP_DEFAULT_ORGANISATION"):
                search = search.filter("term", organisation__pid=view)

            # Filter collection
            if request.args.get("collection_view"):
                search = search.filter("term", collections__pid=request.args["collection_view"])
        # Filters records by user's organisation
        elif not current_user_record.is_superuser:
            search = search.filter("term", organisation__pid=current_organisation["pid"])

    return (search, urlkwargs)
