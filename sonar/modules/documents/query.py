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

"""Query for documents."""

import re

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

    # Special treatment for fulltext, we want to search in all fields and
    # additionally in the fulltext field.
    if "fulltext:" in qstr:
        result = re.match(r"^fulltext:(.*)$", qstr)
        qstr = result.group(1)
    else:
        # remove the fulltext field
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

    # Public search
    if view:
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

        # Filter record by organisation view.
        if view != current_app.config.get("SONAR_APP_DEFAULT_ORGANISATION"):
            search = search.filter("term", organisation__pid=view)

        # Filter collection
        if request.args.get("collection_view"):
            search = search.filter("term", collections__pid=request.args["collection_view"])
    # Admin
    else:
        # Filters records by user's organisation
        if not current_user_record.is_superuser:
            search = search.filter("term", organisation__pid=current_organisation["pid"])

    return (search, urlkwargs)
