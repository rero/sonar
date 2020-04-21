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

from sonar.modules.documents.api import DocumentRecord

from ..api import SonarRecord, SonarSearch
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

    STATUS_IN_PROGRESS = 'in progress'
    STATUS_VALIDATED = 'validated'
    STATUS_TO_VALIDATE = 'to validate'
    STATUS_REJECTED = 'rejected'
    STATUS_ASK_FOR_CHANGES = 'ask for changes'

    REVIEW_ACTION_APPROVE = 'approve'
    REVIEW_ACTION_REJECT = 'reject'
    REVIEW_ACTION_ASK_FOR_CHANGES = 'ask-for-changes'

    minter = deposit_pid_minter
    fetcher = deposit_pid_fetcher
    provider = DepositProvider
    schema = 'deposit'

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
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': action
        }

        if comment:
            log['comment'] = comment

        self['logs'].append(log)

        return log

    def create_document(self):
        """Create document from deposit."""
        metadata = {}

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
        metadata['language'] = [{
            'value': language,
            'type': 'bf:Language'
        }]

        # Document date
        if self['metadata'].get('documentDate'):
            metadata['provisionActivity'] = [{
                'type':
                'bf:Publication',
                'startDate':
                self['metadata']['documentDate']
            }]

        # Published in
        part_of = {
            'numberingYear': self['metadata']['publication']['year'],
            'numberingPages': self['metadata']['publication']['pages'],
            'document': {
                'title': self['metadata']['publication']['publishedIn']
            }
        }
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
                'publicNote': link['type']
            } for link in self['metadata']['otherElectronicVersions']]

        # Specific collections
        if self['metadata'].get('specificCollections'):
            metadata['specificCollections'] = self['metadata'][
                'specificCollections']

        # Classification
        metadata['classification'] = [{
            'type':
            'bf:ClassificationUdc',
            'classificationPortion':
            self['metadata']['classification']
        }]

        # Abstracts
        if self['metadata'].get('abstracts'):
            metadata['abstracts'] = [{
                'language': abstract.get('language', language),
                'value': abstract['abstract']
            } for abstract in self['metadata']['abstracts']]

        # Subjects
        if self['metadata'].get('subjects'):
            metadata['subjects'] = [{
                'label': {
                    'language': subject.get('language', language),
                    'value': subject['subjects']
                }
            } for subject in self['metadata']['subjects']]

        # Contributors
        metadata['contribution'] = [{
            'agent': {
                'type': 'bf:Person',
                'preferred_name': contributor['name']
            },
            'role': ['ctb'],
            'affiliation': contributor['affiliation']
        } for contributor in self['contributors']]

        # Resolve controlled affiliations
        for contributor in metadata['contribution']:
            affiliations = DocumentRecord.get_affiliations(
                contributor['affiliation'])
            if affiliations:
                contributor['controlledAffiliation'] = affiliations

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
                    kwargs['embargo_date'] = file['embargoDate']

                if file.get('exceptInOrganisation'):
                    kwargs['restricted'] = 'organisation'

                document.add_file(content, file['key'], **kwargs)

        document.commit()
        document.reindex()

        self['document'] = {
            '$ref': DocumentRecord.get_ref_link('documents', document['pid'])
        }

        return document
