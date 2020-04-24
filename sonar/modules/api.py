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

"""API for manipulating records."""

import re
from io import BytesIO
from uuid import uuid4

import requests
from flask import current_app
from invenio_db import db
from invenio_files_rest.helpers import compute_md5_checksum
from invenio_indexer.api import RecordIndexer
from invenio_jsonschemas import current_jsonschemas
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_files.api import FilesMixin, Record
from invenio_search.api import RecordsSearch
from sqlalchemy.orm.exc import NoResultFound

from sonar.modules.pdf_extractor.utils import extract_text_from_content
from sonar.modules.utils import change_filename_extension, \
    create_thumbnail_from_file


class SonarRecord(Record, FilesMixin):
    """SONAR Record."""

    minter = None
    fetcher = None
    provider = None
    object_type = 'rec'
    schema = None

    @classmethod
    def create(cls,
               data,
               id_=None,
               dbcommit=False,
               with_bucket=False,
               **kwargs):
        """Create a new record."""
        assert cls.minter
        assert cls.schema

        if not id_:
            id_ = uuid4()

        if '$schema' not in data:
            data["$schema"] = current_jsonschemas.path_to_url(cls.schema)

        cls.minter(id_, data)

        record = super(SonarRecord, cls).create(data=data,
                                                with_bucket=with_bucket,
                                                id_=id_,
                                                **kwargs)

        if dbcommit:
            record.dbcommit()

        return record

    @classmethod
    def get_record_by_pid(cls, pid, with_deleted=False):
        """Get ils record by pid value."""
        assert cls.provider
        try:
            persistent_identifier = PersistentIdentifier.get(
                cls.provider.pid_type, pid)
            return super(SonarRecord,
                         cls).get_record(persistent_identifier.object_uuid,
                                         with_deleted=with_deleted)
        except NoResultFound:
            return None
        except PIDDoesNotExistError:
            return None

    @classmethod
    def get_ref_link(cls, record_type, record_id):
        """Get $ref link for the given type of record."""
        return 'https://{host}/api/{type}/{id}'.format(
            host=current_app.config.get('JSONSCHEMAS_HOST'),
            type=record_type,
            id=record_id)

    @classmethod
    def get_pid_by_ref_link(cls, link):
        """Return the PID corresponding to the ref link given."""
        result = re.match(r'.*\/(.*)$', link)

        if result is None:
            raise Exception('{link} is not a valid ref link'.format(link=link))

        return result.group(1)

    @classmethod
    def get_record_by_ref_link(cls, link):
        """Get a record by its ref link."""
        return cls.get_record_by_pid(cls.get_pid_by_ref_link(link))

    @staticmethod
    def dbcommit():
        """Commit changes to db."""
        db.session.commit()

    def reindex(self):
        """Reindex record."""
        RecordIndexer().index(self)

    def add_file_from_url(self, url, key, **kwargs):
        """Add file to record by getting data from given url.

        :param str url: External URL of the file
        :param str key: File key

        for kwargs, see add_file method below.
        """
        kwargs['url'] = url
        self.add_file(requests.get(url).content, key, **kwargs)

    def add_file(self, data, key, **kwargs):
        """Create file and add it to record.

        :param data: Binary data of file
        :param str key: File key

        kwargs may contain some additional data such as: file label, file type,
        order and url.
        """
        if not current_app.config.get('SONAR_DOCUMENTS_IMPORT_FILES'):
            return

        # If file with the same key exists and checksum is the same as the
        # registered file, we don't do anything
        checksum = compute_md5_checksum(BytesIO(data))
        if key in self.files and checksum == self.files[key].file.checksum:
            return

        # Create the file
        self.files[key] = BytesIO(data)
        self.files[key]['label'] = kwargs.get('label', key)
        self.files[key]['type'] = kwargs.get('type', 'file')
        self.files[key]['order'] = kwargs.get('order', 1)

        # Embargo
        if kwargs.get('restricted'):
            self.files[key]['restricted'] = kwargs['restricted']

        if kwargs.get('embargo_date'):
            self.files[key]['embargo_date'] = kwargs['embargo_date']

        # Store external file URL
        if kwargs.get('url'):
            self.files[key]['external_url'] = kwargs['url']

        # Create thumbnail
        if current_app.config.get('SONAR_DOCUMENTS_GENERATE_THUMBNAIL'):
            self.create_thumbnail(self.files[key])

        # Try to extract full text from file data, and generate a warning if
        # it's not possible. For several cases, file is locked against fulltext
        # copy.
        if current_app.config.get(
                'SONAR_DOCUMENTS_EXTRACT_FULLTEXT_ON_IMPORT'
        ) and self.files[key].mimetype == 'application/pdf':
            try:
                fulltext = extract_text_from_content(data)

                key = change_filename_extension(key, 'txt')
                self.files[key] = BytesIO(fulltext.encode())
                self.files[key]['type'] = 'fulltext'
            except Exception as exception:
                current_app.logger.warning(
                    'Error during fulltext extraction of {file} of record '
                    '{record}: {error}'.format(file=key,
                                               error=exception,
                                               record=self['identifiedBy']))

    def create_thumbnail(self, file=None):
        """Create a thumbnail for record.

        This is done by getting the file with order 1 or the first file
        instead.

        :param file: File from which thumbnail is created.
        """
        # If not file passed, try to get the main file
        if not file:
            file = self.get_main_file()

        # No file found, we don't do anything
        if not file:
            return

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
        files = [file for file in self.files if file['type'] == 'file']

        if not files:
            return None

        for file in files:
            if file.get('type') == 'file' and file.get('order') == 1:
                return file

        return files[0]


class SonarSearch(RecordsSearch):
    """Search Class SONAR."""

    class Meta:
        """Search only on item index."""

        index = 'records'
