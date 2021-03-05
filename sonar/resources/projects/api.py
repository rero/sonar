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

"""API for projects resources."""

from invenio_pidstore.providers.recordid import RecordIdProvider
from invenio_records.dumpers import ElasticsearchDumper, ElasticsearchDumperExt
from invenio_records.systemfields import ConstantField
from invenio_records_resources.records.api import Record as BaseRecord
from invenio_records_resources.records.systemfields import IndexField, PIDField
from invenio_records_resources.services.records.components import \
    ServiceComponent

from sonar.affiliations import AffiliationResolver
from sonar.modules.organisations.api import OrganisationRecord
from sonar.modules.users.api import UserRecord

from . import models


class ElasticsearchDumperObjectsExt(ElasticsearchDumperExt):
    """Interface for Elasticsearch dumper extensions."""

    def dump(self, record, data):
        """Dump the data for indexing."""
        if data['metadata'].get('user'):
            data['metadata']['user'] = {
                'pid':
                UserRecord.get_pid_by_ref_link(
                    data['metadata']['user']['$ref'])
            }

        if data['metadata'].get('organisation'):
            data['metadata']['organisation'] = {
                'pid':
                OrganisationRecord.get_pid_by_ref_link(
                    data['metadata']['organisation']['$ref'])
            }


class Record(BaseRecord):
    """API for projects resources."""

    # Configuration
    model_cls = models.RecordMetadata

    # System fields
    schema = ConstantField(
        '$schema', 'https://sonar.ch/schemas/projects/project-v1.0.0.json')

    index = IndexField('projects-project-v1.0.0', search_alias='projects')

    pid = PIDField('id', pid_type='proj', provider=RecordIdProvider)

    dumper = ElasticsearchDumper(extensions=[ElasticsearchDumperObjectsExt()])


class RecordComponent(ServiceComponent):
    """Custom action for projects records."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Guess controlled affiliations."""
        self._guess_controlled_affiliations(data['metadata'])

    def update(self, identity, data=None, record=None, **kwargs):
        """Guess controlled affiliations."""
        self._guess_controlled_affiliations(data['metadata'])

    def _guess_controlled_affiliations(self, data):
        """Guess controlled affiliations.

        :param data: Record data.
        """
        affiliation_resolver = AffiliationResolver()
        for investigator in data.get('investigators', []):
            if investigator.get('affiliation'):
                controlled_affiliation = affiliation_resolver.resolve(
                    investigator['affiliation'])
                if controlled_affiliation:
                    investigator['controlledAffiliation'] = [
                        controlled_affiliation
                    ]
