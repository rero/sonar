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

"""Deposit API."""

from datetime import datetime
from functools import partial

import pytz
from flask import g

from sonar.modules.api import SonarRecord
from sonar.modules.collections.api import Record as CollectionRecord
from sonar.modules.documents.api import DocumentRecord
from sonar.modules.users.api import UserRecord, current_user_record
from sonar.proxies import sonar

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
        # TODO : Do this whole process with a marshmallow schema serializer.
        metadata = {}

        # Organisation
        if current_user_record and current_user_record.get('organisation'):
            metadata['organisation'] = [current_user_record['organisation']]

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
        metadata['provisionActivity'] = [{
            'type':
            'bf:Publication',
            'startDate':
            self['metadata']['documentDate']
        }]
        metadata['provisionActivity'][0]['statement'] = []

        # Publication place
        if self['metadata'].get('publicationPlace'):
            metadata['provisionActivity'][0]['statement'].append({
                'label': [{
                    'value': self['metadata']['publicationPlace']
                }],
                'type':
                'bf:Place'
            })

        # Publisher
        if self['metadata'].get('publisher'):
            metadata['provisionActivity'][0]['statement'].append({
                'label': [{
                    'value': self['metadata']['publisher']
                }],
                'type':
                'bf:Agent'
            })

        # Add a statement for date
        metadata['provisionActivity'][0]['statement'].append({
            'label': [{
                'value': self['metadata']['documentDate']
            }],
            'type':
            'Date'
        })

        # Published in
        if self['metadata'].get('publication'):
            part_of = {
                'numberingYear': self['metadata']['documentDate'],
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

        # Collections
        if self['metadata'].get('collections'):
            collections = []
            for collection in self['metadata'].get('collections'):
                # Create a new project
                if not collection.get('$ref'):
                    data = collection.copy()
                    # Store organisation
                    data['organisation'] = current_user_record['organisation']
                    collection_record = CollectionRecord.create(data)
                    collection_record.reindex()
                    collection = {
                        '$ref':
                        SonarRecord.get_ref_link('collections',
                                                 collection_record['pid'])
                    }

                collections.append(collection)

            if collections:
                metadata['collections'] = collections

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

                    project_record = sonar.service('projects').create(
                        g.identity, {'metadata': data})
                    project = {
                        '$ref':
                        SonarRecord.get_ref_link('projects',
                                                 project_record['id'])
                    }

                projects.append(project)

            if projects:
                metadata['projects'] = projects

        # License
        metadata['usageAndAccessPolicy'] = {
            'license': self['diffusion']['license']
        }

        # Open access status
        if self['diffusion'].get('oa_status'):
            metadata['oa_status'] = self['diffusion']['oa_status']

        # Subdivisions
        if self['diffusion'].get('subdivisions'):
            metadata['subdivisions'] = self['diffusion']['subdivisions']
        else:
            # Guess from submitter
            user = UserRecord.get_record_by_ref_link(self['user']['$ref'])
            if user and user.is_submitter and user.get('subdivision'):
                metadata['subdivisions'] = [user['subdivision']]

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
