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

"""API for projects resources."""

from invenio_jsonschemas import current_jsonschemas
from invenio_pidstore.providers.recordid import RecordIdProvider as BaseRecordIdProvider
from invenio_records.dumpers import SearchDumper, SearchDumperExt
from invenio_records.systemfields import SystemField
from invenio_records_resources.records.systemfields import IndexField, PIDField
from invenio_records_resources.services.records.components import ServiceComponent

from sonar.affiliations import AffiliationResolver
from sonar.modules.organisations.api import OrganisationRecord
from sonar.modules.users.api import UserRecord
from sonar.modules.utils import get_pid_from_ref_or_data
from sonar.modules.validation.extensions.validation import ValidationExtension
from sonar.resources.api import Record as BaseRecord

from . import models

# Custom provider to set the PID type
RecordIdProvider = type("RecordIdProvider", (BaseRecordIdProvider,), {"pid_type": "proj"})


class SearchDumperObjectsExt(SearchDumperExt):
    """Interface for Elasticsearch dumper extensions."""

    def dump(self, record, data):
        """Dump the data for indexing."""
        if data["metadata"].get("user"):
            data["metadata"]["user"] = {"pid": UserRecord.get_pid_by_ref_link(data["metadata"]["user"]["$ref"])}

        if data["metadata"].get("organisation"):
            organisation = OrganisationRecord.get_record_by_ref_link(data["metadata"]["organisation"]["$ref"])
            data["metadata"]["organisation"] = {
                "pid": organisation["pid"],
                "name": organisation["name"],
            }


class JSONSchemaField(SystemField):
    """JSON Schema system field."""

    def pre_commit(self, record):
        """Change the $schema before validation."""
        record["$schema"] = self._get_schema(record)

    def _get_schema(self, data):
        """Get the JSON schema URL for the record."""
        schema_url = current_jsonschemas.path_to_url("projects/project-v1.0.0.json")
        if org := data.get("metadata", {}).get("organisation"):
            current_organisation = get_pid_from_ref_or_data(org)
            schema_url = (
                current_jsonschemas.path_to_url(f"{current_organisation}/projects/project-v1.0.0.json") or schema_url
            )
        return schema_url


class Record(BaseRecord):
    """API for projects resources."""

    # Configuration
    model_cls = models.RecordMetadata

    # System fields
    index = IndexField("projects-project-v1.0.0", search_alias="projects")

    # The `pid_type` must not be filled as argument in this constructor.
    # Instead it is guessed from RecordIdProvider.
    pid = PIDField("id", provider=RecordIdProvider)

    # PID type retrieved from provider
    pid_type = RecordIdProvider.pid_type

    dumper = SearchDumper(extensions=[SearchDumperObjectsExt()])

    _extensions = [ValidationExtension()]

    schema = JSONSchemaField("$schema")

    def __repr__(self):
        """String representation of object.

        :returns: A string representing the object.
        """
        return self["metadata"]["name"]


class RecordComponent(ServiceComponent):
    """Custom action for projects records."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Guess controlled affiliations."""
        self._guess_controlled_affiliations(data["metadata"])

    def update(self, identity, data=None, record=None, **kwargs):
        """Guess controlled affiliations."""
        self._guess_controlled_affiliations(data["metadata"])

    def _guess_controlled_affiliations(self, data):
        """Guess controlled affiliations.

        :param data: Record data.
        """
        affiliation_resolver = AffiliationResolver()
        for investigator in data.get("investigators", []):
            if investigator.get("affiliation"):
                controlled_affiliations = affiliation_resolver.resolve(investigator["affiliation"])
                if controlled_affiliations:
                    investigator["controlledAffiliation"] = controlled_affiliations
