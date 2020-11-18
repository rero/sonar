# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2019 RERO
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

"""Deposit API."""

from datetime import datetime
from functools import partial

import pytz

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.projects.api import ProjectRecord
from sonar.modules.users.api import current_user_record

from ..api import SonarIndexer, SonarRecord, SonarSearch
from ..fetchers import id_fetcher
from ..minters import id_minter
from ..providers import Provider

# provider
DepositProvider = type('DepositProvider', (Provider, ), dict(pid_type='depo'))
# minter
deposit_pid_minter = partial(id_minter, provider=DepositProvider)
# fetcher
deposit_pid_fetcher = partial(id_fetcher, provider=DepositProvider)


class DepositSearch(SonarSearch):
    """Search deposits."""

    class Meta:
        """Search only on item index."""

        index = 'deposits'
        doc_types = []


class DepositRecord(SonarRecord):
    """Deposit record class."""

    STEP_DIFFUSION = 'diffusion'

    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_VALIDATED = 'validated'
    STATUS_TO_VALIDATE = 'to_validate'
    STATUS_REJECTED = 'rejected'
    STATUS_ASK_FOR_CHANGES = 'ask_for_changes'

    REVIEW_ACTION_APPROVE = 'approve'
    REVIEW_ACTION_REJECT = 'reject'
    REVIEW_ACTION_ASK_FOR_CHANGES = 'ask_for_changes'

    minter = deposit_pid_minter
    fetcher = deposit_pid_fetcher
    provider = DepositProvider
    schema = 'deposits/deposit-v1.0.0.json'

    @classmethod
    def create(cls, data, id_=None, dbcommit=False, with_bucket=True,
               **kwargs):
        """Create deposit record."""
        record = super(DepositRecord, cls).create(data,
                                                  id_=id_,
                                                  dbcommit=dbcommit,
                                                  with_bucket=with_bucket,
                                                  **kwargs)
        return record

    def log_action(self, user, action, comment=None):
        """Log intervention into deposit."""
        if 'logs' not in self:
            self['logs'] = []

        log = {
            'user': user,
            'date': pytz.utc.localize(datetime.utcnow()).isoformat(),
            'action': action
        }

        if comment:
            log['comment'] = comment

        self['logs'].append(log)

        return log

    def create_document(self):
        """Create document from deposit."""
        metadata = {}

        # Organisation
        if current_user_record and current_user_record.get('organisation'):
            metadata['organisation'] = current_user_record['organisation']

        # Document type
        metadata['documentType'] = self['metadata']['documentType']

        # Language
        language = self['metadata'].get('language', 'eng')

        # Title
        metadata['title'] = [{
            'type':
            'bf:Title',
            'mainTitle': [{
                'language': language,
                'value': self['metadata']['title']
            }]
        }]

        # Subtitle
        if self['metadata'].get('subtitle'):
            metadata['title'][0]['subtitle'] = [{
                'language':
                language,
                'value':
                self['metadata']['subtitle']
            }]

        # Other title
        if self['metadata'].get('otherLanguageTitle', {}).get('title'):
            metadata['title'][0]['mainTitle'].append({
                'language':
                self['metadata']['otherLanguageTitle'].get(
                    'language', language),
                'value':
                self['metadata']['otherLanguageTitle']['title']
            })

        # Languages
        metadata['language'] = [{'value': language, 'type': 'bf:Language'}]

        # Document date
        if self['metadata'].get('documentDate'):
            metadata['provisionActivity'] = [{
                'type':
                'bf:Publication',
                'startDate':
                self['metadata']['documentDate']
            }]

        # Published in
        if self['metadata'].get('publication'):
            part_of = {
                'numberingYear': self['metadata']['publication']['year'],
                'document': {
                    'title': self['metadata']['publication']['publishedIn']
                }
            }

            if self['metadata']['publication'].get('pages'):
                part_of['numberingPages'] = self['metadata']['publication'][
                    'pages']

            if self['metadata']['publication'].get('volume'):
                part_of['numberingVolume'] = self['metadata']['publication'][
                    'volume']

            if self['metadata']['publication'].get('number'):
                part_of['numberingIssue'] = self['metadata']['publication'][
                    'number']

            if self['metadata']['publication'].get('editors'):
                part_of['document']['contribution'] = self['metadata'][
                    'publication']['editors']

            if self['metadata']['publication'].get('publisher'):
                part_of['document']['publication'] = {
                    'statement': self['metadata']['publication']['publisher']
                }

            metadata['partOf'] = [part_of]

        # Other electronic versions
        if self['metadata'].get('otherElectronicVersions'):
            metadata['otherEdition'] = [{
                'document': {
                    'electronicLocator': link['url']
                },
                'publicNote': link['publicNote']
            } for link in self['metadata']['otherElectronicVersions']]

        # Specific collections
        if self['metadata'].get('specificCollections'):
            metadata['specificCollections'] = self['metadata'][
                'specificCollections']

        # Classification
        if self['metadata'].get('classification'):
            metadata['classification'] = [{
                'type':
                'bf:ClassificationUdc',
                'classificationPortion':
                self['metadata']['classification']
            }]

        # Abstracts
        if self['metadata'].get('abstracts'):
            metadata['abstracts'] = [{
                'language':
                abstract.get('language', language),
                'value':
                abstract['abstract']
            } for abstract in self['metadata']['abstracts']]

        # Dissertation
        if self['metadata'].get('dissertation'):
            metadata['dissertation'] = self['metadata']['dissertation']

        # Subjects
        if self['metadata'].get('subjects'):
            metadata['subjects'] = [{
                'label': {
                    'language': subject.get('language', language),
                    'value': subject['subjects']
                }
            } for subject in self['metadata']['subjects']]

        # Identifiers
        identifiers = []
        if self['metadata'].get('identifiedBy'):
            for identifier in self['metadata']['identifiedBy']:
                data = {
                    'type': identifier['type'],
                    'value': identifier['value'],
                }

                if identifier.get('source'):
                    data['source'] = identifier['source']

                # Special for PMID
                if identifier['type'] == 'pmid':
                    data['source'] = 'PMID'
                    data['type'] = 'bf:Local'

                identifiers.append(data)

        if identifiers:
            metadata['identifiedBy'] = identifiers

        # Contributors
        contributors = []
        for contributor in self.get('contributors', []):
            data = {
                'agent': {
                    'type': 'bf:Person',
                    'preferred_name': contributor['name']
                },
                'role': [contributor['role']]
            }

            if contributor.get('affiliation'):
                data['affiliation'] = contributor['affiliation']

            # ORCID for contributor
            if contributor.get('orcid'):
                data['agent']['identifiedBy'] = {
                    'type': 'bf:Local',
                    'source': 'ORCID',
                    'value': contributor['orcid']
                }

            contributors.append(data)

        if contributors:
            metadata['contribution'] = contributors

        # Projects
        if self.get('projects'):
            projects = []

            for project in self['projects']:
                # Create a new project
                if not project.get('$ref'):
                    data = project.copy()

                    # Store user
                    data['user'] = self['user']

                    # Store organisation
                    data['organisation'] = current_user_record['organisation']

                    # Project identifier
                    if project.get('identifier'):
                        data['identifiedBy'] = {
                            'type': 'bf:Identifier',
                            'value': project['identifier']
                        }
                        data.pop('identifier')

                    # Investigators
                    if project.get('investigators'):
                        data['investigators'] = []
                        for investigator in project['investigators']:
                            investigator_data = {
                                'agent': {
                                    'preferred_name': investigator['name']
                                },
                                'role': [investigator['role']],
                            }

                            if investigator.get('affiliation'):
                                investigator_data[
                                    'affiliation'] = investigator.get(
                                        'affiliation')

                            if investigator.get('orcid'):
                                investigator_data['identifiedBy'] = {
                                    'type': 'bf:Local',
                                    'source': 'ORCID',
                                    'value': investigator.get('orcid')
                                }

                            data['investigators'].append(investigator_data)

                    # Funding organisations
                    if project.get('funding_organisations'):
                        data['funding_organisations'] = []
                        for funding_organisation in project[
                                'funding_organisations']:
                            funding_organisation_data = {
                                'agent': {
                                    'preferred_name':
                                    funding_organisation['name']
                                }
                            }

                            if funding_organisation.get('identifier'):
                                funding_organisation_data['identifiedBy'] = {
                                    'type': 'bf:Identifier',
                                    'value': funding_organisation['identifier']
                                }

                            data['funding_organisations'].append(
                                funding_organisation_data)

                    project_record = ProjectRecord.create(data, dbcommit=True)
                    project_record.reindex()
                    project = {
                        '$ref':
                        project_record.get_ref_link('projects',
                                                    project_record['pid'])
                    }

                projects.append(project)

            if projects:
                metadata['projects'] = projects

        # License
        metadata['usageAndAccessPolicy'] = {
            'license': self['diffusion']['license']
        }

        document = DocumentRecord.create(metadata,
                                         dbcommit=True,
                                         with_bucket=True)

        current_order = 2
        for file in self.files:
            with file.file.storage().open() as pdf_file:
                content = pdf_file.read()

                if file.get('category', 'main') == 'main':
                    order = 1
                else:
                    order = current_order
                    current_order += 1

                kwargs = {
                    'label': file.get('label', file['key']),
                    'order': order
                }

                if file.get('embargo', False) and file.get('embargoDate'):
                    kwargs['access'] = 'coar:c_f1cf'  # Embargoed access
                    kwargs['embargo_date'] = file['embargoDate']
                    kwargs['restricted_outside_organisation'] = file.get(
                        'exceptInOrganisation', False)

                document.add_file(content, file['key'], **kwargs)

        document.commit()
        document.reindex()

        self['document'] = {
            '$ref': DocumentRecord.get_ref_link('documents', document['pid'])
        }

        return document


class DepositIndexer(SonarIndexer):
    """Indexing documents in Elasticsearch."""

    record_cls = DepositRecord
