# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Projects service."""

import contextlib

from flask import current_app
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

from sonar.modules.api import SonarIndexer
from sonar.modules.utils import get_pid_from_ref_or_data

from ..service import RecordService, RecordServiceConfig
from .api import Record, RecordComponent
from .permissions import RecordPermissionPolicy
from .results import RecordList


class ProjectIndexer(SonarIndexer):
    """Project indexer."""

    record_cls = Record


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


class ConfiguredFacets:
    """Provide dynamically configured facets as a class property.

    Invenio accesses facets directly from the SearchOptions class. This
    descriptor builds them on access using the current application
    configuration.
    """

    def __get__(self, obj, objtype=None):
        """Build facets using the current application configuration."""
        sizes = {
            "size": current_app.config["SONAR_APP_AGGREGATION_SIZE"],
            "shard_size": current_app.config["SONAR_APP_AGGREGATION_SHARD_SIZE"],
        }

        return {
            "user": TermsFacet(field="metadata.user.pid", **sizes),
            "organisation": TermsFacet(field="metadata.organisation.pid", **sizes),
            "status": TermsFacet(field="metadata.validation.status", **sizes),
        }


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

    facets = ConfiguredFacets()

    suggest_parser_cls = SuggestQueryParser.factory(
        fields=[
            "metadata.name.suggest",
            "metadata.projectSponsor",
            "metadata.innerSearcher",
            "metadata.keywords",
        ]
    )


class ProjectsRecordServiceConfig(RecordServiceConfig):
    """Projects service configuration."""

    permission_policy_cls = RecordPermissionPolicy

    record_cls = Record
    indexer_cls = ProjectIndexer

    result_list_cls = RecordList

    search = SearchOptions

    components = [*RecordServiceConfig.components, RecordComponent]


class ProjectServiceSchemaWrapper(ServiceSchemaWrapper):
    """Schema wrapper injecting the organisation into project data."""

    def _get_organisation_pid(self, data):
        """Get organisation PID from data."""
        if org := data.get("metadata", {}).get("organisation"):
            return get_pid_from_ref_or_data(org)
        return None

    def _set_schema(self, data):
        if organisation_pid := self._get_organisation_pid(data):
            with contextlib.suppress(ImportError):
                self.schema = obj_or_import_string(f"sonar.dedicated.{organisation_pid}.projects.schema:RecordSchema")

    def load(self, data, schema_args=None, context=None, raise_errors=True):
        """Load data with dynamic schema_args + context + raise or not."""
        self._set_schema(data)
        return super().load(data, schema_args, context, raise_errors)

    def dump(self, data, schema_args=None, context=None):
        """Dump data using wrapped schema and dynamic schema_args + context."""
        self._set_schema(data)
        return super().dump(data, schema_args, context)


class ProjectsRecordService(RecordService):
    """Projects service."""

    default_config = ProjectsRecordServiceConfig

    @property
    def schema(self):
        """Returns the data schema instance."""
        schema = obj_or_import_string("sonar.resources.projects.schema:RecordSchema")

        return ProjectServiceSchemaWrapper(self, schema=schema)
