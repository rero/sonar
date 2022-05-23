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

"""Document Api."""


import contextlib
from datetime import datetime
from functools import partial
from io import BytesIO

from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Q
from flask import current_app, request
from invenio_stats import current_stats

from sonar.affiliations import AffiliationResolver
from sonar.modules.documents.minters import id_minter
from sonar.modules.pdf_extractor.utils import extract_text_from_content
from sonar.modules.utils import change_filename_extension, \
    create_thumbnail_from_file, get_current_ip, is_ip_in_list

from ..api import SonarIndexer, SonarRecord, SonarSearch
from ..ark.api import current_ark
from ..fetchers import id_fetcher
from ..providers import Provider
from .extensions import ArkDocumentExtension, UrnDocumentExtension

# provider
DocumentProvider = type('DocumentProvider', (Provider, ), dict(pid_type='doc'))
# minter
document_pid_minter = partial(id_minter, provider=DocumentProvider)
# fetcher
document_pid_fetcher = partial(id_fetcher, provider=DocumentProvider)


class DocumentSearch(SonarSearch):
    """Search documents."""

    class Meta:
        """Search only on item index."""

        index = 'documents'
        doc_types = []

class DocumentRecord(SonarRecord):
    """Document record class."""

    minter = document_pid_minter
    fetcher = document_pid_fetcher
    provider = DocumentProvider
    schema = 'documents/document-v1.0.0.json'
    _extensions = [ArkDocumentExtension(), UrnDocumentExtension()]

    @staticmethod
    def get_permanent_link(host, pid, org=None):
        """Return the permanent link for the document.

        :param host: Application server host.
        :param org: Organisation key.
        :param pid: PID of the document.
        :returns: Document's full URL as string.
        """
        if not org:
            org = current_app.config.get('SONAR_APP_DEFAULT_ORGANISATION')

        return current_app.config.get('SONAR_DOCUMENTS_PERMALINK').format(
            host=host, org=org, pid=pid)

    @staticmethod
    def get_documents_by_project(project_pid):
        """Return the list of documents associated to the given project.

        :param project_pid: PID of the project.
        :returns: List of documents matching the project PID.
        """

        def format_hit(hit):
            """Format hit item."""
            hit = hit.to_dict()
            hit['permalink'] = DocumentRecord.get_permanent_link(
                request.host_url, hit['pid'])
            return hit

        results = DocumentSearch().filter(
            'term',
            projects__pid=project_pid).source(includes=['pid', 'title'])
        return list(map(format_hit, results))

    @classmethod
    def create(cls, data, id_=None, dbcommit=False, with_bucket=True,
               **kwargs):
        """Create document record."""
        cls.guess_controlled_affiliations(data)
        return super(DocumentRecord, cls).create(data,
                                                 id_=id_,
                                                 dbcommit=dbcommit,
                                                 with_bucket=with_bucket,
                                                 **kwargs)

    @classmethod
    def guess_controlled_affiliations(cls, data):
        """Guess controlled affiliations.

        :param data: Record data.
        """
        affiliation_resolver = AffiliationResolver()
        for contributor in data.get('contribution', []):
            # remove existing controlled affiliation
            contributor.pop('controlledAffiliation', None)
            if contributor.get('affiliation'):
                if controlled_affiliations := affiliation_resolver.resolve(
                        contributor['affiliation']):
                    contributor[
                        'controlledAffiliation'] = controlled_affiliations



    @classmethod
    def get_record_by_identifier(cls, identifiers):
        """Get a record by its identifier.

        :param list identifiers: List of identifiers
        """
        search = DocumentSearch()

        # Search only for DOI or local indeitifiers.
        search_identifiers = [
            identifier for identifier in identifiers
            if identifier['type'] in ['bf:Local', 'bf:Doi']
        ]

        # No identifiers to analyze
        if not search_identifiers:
            return None

        # Construct filters to match the whole identifier (type, value and
        # source). This is possible by configuring the property as `nested`
        filters = []
        for identifier in search_identifiers:
            identifier_filters = [
                Q('term', identifiedBy__value=identifier['value']),
                Q('term', identifiedBy__type=identifier['type'])
            ]
            if identifier.get('source'):
                identifier_filters.append(
                    Q('term', identifiedBy__source=identifier['source']))

            filters.append(
                Q('nested',
                  path='identifiedBy',
                  query=Q('bool', filter=identifier_filters)))

        search = search.query('bool', filter=filters).source(includes=['pid'])
        results = list(search)
        if results:
            return cls.get_record_by_pid(results[0]['pid'])

        return None

    def add_file(self, data, key, **kwargs):
        """Create file and add it to record.

        kwargs may contain some additional data such as: file label, file type,
        order and url.

        :param data: Binary data of file
        :param str key: File key
        :returns: File object created.
        """
        if not kwargs.get('type'):
            kwargs['type'] = 'file'

        if not kwargs.get('order'):
            kwargs['order'] = self.get_next_file_order()

        if not kwargs.get('label'):
            kwargs['label'] = key

        added_file = super(DocumentRecord, self).add_file(data, key, **kwargs)

        if not added_file:
            return None

        self.create_fulltext_file(self.files[key])
        self.create_thumbnail(self.files[key])

        return self.files[key]

    def sync_files(self, file, deleted=False):
        """Sync files between bucket and records.

        This operation is necessary to make files available in record detail
        and be indexed.

        :param file: File object.
        :param deleted: Wether the given file has been deleted or not.
        """
        # Synchronise files between bucket and record.
        self.files.flush()

        # If file is not deleted, a thumbnail and a fulltext file is generated.
        if not deleted:
            self.create_fulltext_file(self.files[file.key])
            self.create_thumbnail(self.files[file.key])

            # Default type is `file`
            if not self.files[file.key].get('type'):
                self.files[file.key]['type'] = 'file'

            # Default label is `file.key`
            if not self.files[file.key].get('label'):
                self.files[file.key]['label'] = file.key

            # Order is calculated with other files
            if not self.files[file.key].get('order'):
                self.files[file.key]['order'] = self.get_next_file_order()

        super(DocumentRecord, self).sync_files(file, deleted)

    def create_fulltext_file(self, file):
        """Create fulltext file corresponding to give file object.

        :param file: File object.
        """
        # If extract fulltext is disabled or file is not a PDF
        if not current_app.config.get(
                'SONAR_DOCUMENTS_EXTRACT_FULLTEXT_ON_IMPORT'
        ) or file.mimetype != 'application/pdf':
            return

        # Try to extract full text from file data, and generate a warning if
        # it's not possible. For several cases, file is locked against fulltext
        # copy.
        try:
            with file.file.storage().open() as pdf_file:
                fulltext = extract_text_from_content(pdf_file.read())

            key = change_filename_extension(file.key, 'txt')
            self.files[key] = BytesIO(fulltext.encode())
            self.files[key]['type'] = 'fulltext'
        except Exception as exception:
            current_app.logger.warning(
                'Error during fulltext extraction of {file} of record '
                '{record}: {error}'.format(file=file.key,
                                           error=exception,
                                           record=self['identifiedBy']))

    def create_thumbnail(self, file):
        """Create a thumbnail for record.

        This is done by getting the file with order 1 or the first file
        instead.

        :param file: File from which thumbnail is created.
        """
        try:
            # Create thumbnail
            image_blob = create_thumbnail_from_file(file.file.uri,
                                                    file.mimetype)

            thumbnail_key = change_filename_extension(file['key'], 'jpg')

            # Store thumbnail in record's files
            self.files[thumbnail_key] = BytesIO(image_blob)
            self.files[thumbnail_key]['type'] = 'thumbnail'
        except Exception as exception:
            current_app.logger.warning(
                'Error during thumbnail generation of {file} of record '
                '{record}: {error}'.format(file=file['key'],
                                           error=exception,
                                           record=self.get(
                                               'identifiedBy', self['pid'])))

    def get_main_file(self):
        """Get the main file of record."""
        files = [file for file in self.files if file.get('type') == 'file']

        if not files:
            return None

        for file in files:
            if file.get('order') == 1:
                return file

        return files[0]

    def get_next_file_order(self):
        """Get position for the next file.

        :returns: Integer representing the new position.
        """
        files = [file for file in self.files if file.get('type') == 'file']

        if not files:
            return 1

        positions = [file.get('order', 1) for file in files]

        return max(positions) + 1

    def get_files_list(self):
        """Return the list of files.

        The files are ordered by `order` property and filtered by `type` with
        value `file`.

        :returns: Formatted list of files.
        """
        files = [
            file for file in self.get('_files', [])
            if file.get('type') == 'file'
        ]
        return sorted(files, key=lambda file: file.get('order', 100))

    def update(self, data):
        """Update record.

        :param data: Record data.
        :returns: Record instance
        """
        self.guess_controlled_affiliations(data)
        return super(DocumentRecord, self).update(data)

    def is_open_access(self):
        """Check if current document is open access.

        :returns: True if the document is open access.
        """
        # No file, means not open access.
        if not self.files:
            return False

        for file in self.files:
            # Restricted access.
            if file.get('access') == 'coar:c_16ec':
                return False

            # Embargoed access
            if file.get('access') == 'coar:c_f1cf':
                if not file.get('embargo_date'):
                    return False

                try:
                    embargo_date = datetime.strptime(file['embargo_date'],
                                                     '%Y-%m-%d')
                except Exception:
                    return False

                return embargo_date <= datetime.now()

        return True

    @property
    def is_masked(self):
        """Check if record is masked.

        :returns: True if record is masked
        :rtype: boolean
        """
        if not self.get('masked'):
            return False

        if self['masked'] == 'masked_for_all':
            return True

        if self['masked'] == 'masked_for_external_ips' and self.get(
                'organisation') and not is_ip_in_list(
                    get_current_ip(), self['organisation'][0].get(
                        'allowedIps', '').split('\n')):
            return True

        return False

    @property
    def statistics(self):
        """Collect the statistics.

        Collect the number of view for a given record (detailed view)
        and the number of download for the related files.

        :returns: the collected statistics
        :rtype: dict
        """
        res = {}
        query_cfg = current_stats.queries['record-view']
        query  = query_cfg.cls(name='record-view', **query_cfg.params)
        try:
            res['record-view'] = int(query.run(pid_type='doc', pid_value=self['pid'])['unique_count'])
        except NotFoundError:
            res['record-view'] = 0
        query_cfg = current_stats.queries['file-download']
        query  = query_cfg.cls(name='file-download', **query_cfg.params)
        res['file-download'] = {f['key']: 0 for f in self.get_files_list()}
        with contextlib.suppress(NotFoundError):
            res_query = query.run(bucket_id=self.bucket_id)
            file_keys = res['file-download'].keys()
            for b in res_query['buckets']:
                if b.get('key') in file_keys:
                    res['file-download'][b['key']] = int(b['unique_count'])
        return res


    def get_ark_resolver_url(self):
        """Get the ark resolver url.

        :returns: the URL to resolve the current identifier.
        """
        if self.get('ark'):
            return current_ark.resolver_url(self.get('pid'))


    @classmethod
    def get_urn_codes(cls, record):
        """Get list of urn codes for document.

        :param record: dictionary of document.
        :returns: list of urns codes.
        """
        return [identifier['value'] for identifier in record.get(
            'identifiedBy', []) if identifier['type'] == 'bf:Urn']


class DocumentIndexer(SonarIndexer):
    """Indexing documents in Elasticsearch."""

    record_cls = DocumentRecord
