# -*- coding: utf-8 -*-
#
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

"""Projects service."""

from invenio_records_resources.services import SearchOptions as BaseSearchOptions
from invenio_records_resources.services.records.facets import TermsFacet
from invenio_records_resources.services.records.params import (
    FacetsParam,
    PaginationParam,
    QueryStrParam,
    SortParam,
)
from invenio_records_resources.services.records.params.querystr import (
    SuggestQueryParser,
)
from invenio_records_resources.services.records.schema import ServiceSchemaWrapper
from invenio_records_rest.utils import obj_or_import_string

from sonar.modules.organisations.api import current_organisation
from sonar.modules.utils import has_custom_resource

from ..service import RecordService, RecordServiceConfig
from .api import Record, RecordComponent
from .permissions import RecordPermissionPolicy
from .results import RecordList


class PreFacetsParam(FacetsParam):
    """."""

    def filter(self, search):
        """Apply a pre filter on the search."""
        if not self._filters:
            return search

        filters = list(self._filters.values())

        post_filter = filters[0]
        for f in filters[1:]:
            post_filter |= f

        return search.filter(post_filter)


class SearchOptions(BaseSearchOptions):
    """Search options."""

    sort_default = "relevance"
    sort_default_no_query = "newest"
    sort_options = {
        "relevance": {
            "fields": ["_score"],
        },
        "name": {"fields": ["metadata.name.raw"]},
        "newest": {"fields": ["-metadata.startDate"]},
        "oldest": {"fields": ["metadata.startDate"]},
    }

    pagination_options = {"default_results_per_page": 10, "default_max_results": 10000}

    params_interpreters_cls = [
        QueryStrParam,
        PaginationParam,
        SortParam,
        PreFacetsParam,
    ]

    facets = {
        "user": TermsFacet(field="metadata.user.pid"),
        "organisation": TermsFacet(field="metadata.organisation.pid"),
        "status": TermsFacet(field="metadata.validation.status"),
    }

    suggest_parser_cls = SuggestQueryParser.factory(
        fields=[
            "metadata.name.suggest",
            "metadata.projectSponsor.suggest",
            "metadata.innerSearcher.suggest",
            "metadata.keywords.suggest",
        ]
    )


class ProjectsRecordServiceConfig(RecordServiceConfig):
    """Projects service configuration."""

    permission_policy_cls = RecordPermissionPolicy

    record_cls = Record

    result_list_cls = RecordList

    search = SearchOptions

    components = RecordServiceConfig.components + [RecordComponent]


class ProjectsRecordService(RecordService):
    """Projects service."""

    default_config = ProjectsRecordServiceConfig

    @property
    def schema(self):
        """Returns the data schema instance."""
        schema_path = "sonar.resources.projects.schema:RecordSchema"

        if has_custom_resource("projects"):
            schema_path = (
                f'sonar.dedicated.{current_organisation["code"]}.'
                "projects.schema:RecordSchema"
            )

        schema = obj_or_import_string(schema_path)

        return ServiceSchemaWrapper(self, schema=schema)
