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

"""Document Api."""

from functools import partial
from io import BytesIO

from flask import current_app, request

from sonar.affiliations import AffiliationResolver
from sonar.modules.documents.minters import id_minter
from sonar.modules.pdf_extractor.utils import extract_text_from_content
from sonar.modules.utils import change_filename_extension, \
    create_thumbnail_from_file

from ..api import SonarIndexer, SonarRecord, SonarSearch
from ..fetchers import id_fetcher
from ..providers import Provider

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
            if contributor.get('affiliation'):
                controlled_affiliation = affiliation_resolver.resolve(
                    contributor['affiliation'])
                if controlled_affiliation:
                    contributor['controlledAffiliation'] = [
                        controlled_affiliation
                    ]

    @classmethod
    def get_record_by_identifier(cls, identifiers):
        """Get a record by its identifier.

        :param list identifiers: List of identifiers
        """
        for identifier in identifiers:
            if identifier['type'] == 'bf:Local':
                results = list(DocumentSearch().filter(
                    'term', identifiedBy__value=identifier['value']).source(
                        includes=['pid']))

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


class DocumentIndexer(SonarIndexer):
    """Indexing documents in Elasticsearch."""

    record_cls = DocumentRecord
