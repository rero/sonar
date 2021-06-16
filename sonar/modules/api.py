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

"""API for manipulating records."""

import os.path
import re
from io import BytesIO
from uuid import uuid4

import requests
from flask import current_app
from invenio_db import db
from invenio_files_rest.helpers import compute_md5_checksum
from invenio_indexer import current_record_to_index
from invenio_indexer.api import RecordIndexer
from invenio_jsonschemas import current_jsonschemas
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records_files.api import FileObject as InvenioFileObjet
from invenio_records_files.api import FilesMixin as InvenioFilesMixin
from invenio_records_files.api import Record
from invenio_records_files.models import RecordsBuckets
from invenio_records_rest.utils import obj_or_import_string
from invenio_search import current_search
from invenio_search.api import RecordsSearch
from sqlalchemy.orm.exc import NoResultFound


class FileObject(InvenioFileObjet):
    """Wrapper for files."""

    def dumps(self):
        """Create a dump of the metadata associated to the record."""
        super(FileObject, self).dumps()
        self.data.update({'mimetype': self.obj.mimetype})
        return self.data


class FilesMixin(InvenioFilesMixin):
    """Implement files attribute for Record models."""

    file_cls = FileObject


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
    def get_indexer_class(cls):
        """Get the indexer from config."""
        return obj_or_import_string(
            current_app.config['RECORDS_REST_ENDPOINTS'][
                cls.provider.pid_type]['indexer_class'])

    @classmethod
    def get_record_class_by_pid_type(cls, pid_type):
        """Get the record class from config by the given PID type.

        :param pid_type: PID type.
        :returns: Record class.
        """
        return current_app.config.get('RECORDS_REST_ENDPOINTS',
                                      {}).get(pid_type, {}).get('record_class')

    @classmethod
    def get_all_pids(cls, with_deleted=False):
        """Get all records pids.

        :param with_deleted: Include deleted records.
        :returns: A generator iterator.
        """
        query = PersistentIdentifier.query.filter_by(
            pid_type=cls.provider.pid_type)
        if not with_deleted:
            query = query.filter_by(status=PIDStatus.REGISTERED)

        for identifier in query:
            yield identifier.pid_value

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

    @classmethod
    def get_persistent_identifier(cls, identifier):
        """Get persistent identifier object.

        :param identifier: Record UUID.
        :returns: PID instance of record.
        """
        return PersistentIdentifier.get_by_object(cls.provider.pid_type,
                                                  cls.object_type, identifier)

    @staticmethod
    def dbcommit():
        """Commit changes to db."""
        db.session.commit()

    @staticmethod
    def get_record_by_bucket(bucket):
        """Find a record by the given bucket.

        :param bucket: Bucket ID.
        :returns: Record corresponding to bucket or None.
        """
        try:
            # Find the record bucket object.
            try:
                records_buckets = RecordsBuckets.query.filter_by(
                    bucket_id=bucket).first()
            except Exception:
                raise Exception('`records_buckets` object not found.')

            # Find the record PID.
            pid = PersistentIdentifier.query.filter_by(
                object_uuid=records_buckets.record_id).filter(
                    ~PersistentIdentifier.pid_type.in_(['oai', 'rerod'])
                ).first()

            if not pid:
                raise Exception('Persistent identifier not found.')

            # Retrieve real record class
            record_class = current_app.config.get(
                'RECORDS_REST_ENDPOINTS',
                {}).get(pid.pid_type).get('record_class')

            if not record_class:
                raise Exception('Class for record not found.')

            record_class = obj_or_import_string(record_class)

            # Load record by its PID.
            return record_class.get_record_by_pid(pid.pid_value)
        except Exception:
            return None

    def reindex(self):
        """Reindex record."""
        indexer = self.get_indexer_class()
        indexer().index(self)

    def add_file_from_url(self, url, key, **kwargs):
        """Add file to record by getting data from given url.

        :param str url: External URL of the file
        :param str key: File key

        for kwargs, see add_file method below.
        """
        kwargs['external_url'] = url
        result = requests.get(url)
        if result.status_code == 200:
            self.add_file(result.content, key, **kwargs)
        else:
            # File cannot be downloaded, keep the link to the external source.
            # And create an empty file.
            kwargs['force_external_url'] = True
            self.add_file(b'', key, **kwargs)

    def add_file(self, data, key, **kwargs):
        """Create file and add it to record.

        kwargs may contain some additional data such as: file label, file type,
        order and url.

        :param data: Binary data of file
        :param str key: File key
        :returns: File object created.
        """
        if not current_app.config.get('SONAR_DOCUMENTS_IMPORT_FILES'):
            return

        # If file with the same key exists and file exists and checksum is
        # the same as the registered file, we don't do anything
        checksum = compute_md5_checksum(BytesIO(data))
        if key in self.files and os.path.isfile(
                self.files[key].file.uri
        ) and checksum == self.files[key].file.checksum:
            return None

        # Create the file
        self.files[key] = BytesIO(data)

        for kwarg_key, kwarg_value in kwargs.items():
            self.files[key][kwarg_key] = kwarg_value

        return self.files[key]

    def sync_files(self, file, deleted=False):
        """Sync files between bucket and records.

        This operation is necessary to make files available in record detail
        and be indexed.

        :param file: File object.
        :param deleted: Wether the given file has been deleted or not.
        """
        # Update record metadata with files.
        self.files.flush()

        # Store metadata in DB.
        self.commit()
        db.session.commit()

        # Re-index record.
        self.reindex()

    def delete(self, force=False, dbcommit=False, delindex=False):
        """Delete record and persistent identifier.

        :param force: Boolean to hard or soft delete.
        :param dbcommit: Boolean for validating database transaction.
        :param delindex: Boolean for deleting the record from index.
        """
        persistent_identifier = self.get_persistent_identifier(self.id)
        persistent_identifier.delete()

        super(SonarRecord, self).delete(force=force)

        if dbcommit:
            self.dbcommit()

        if delindex:
            indexer = self.get_indexer_class()
            indexer().delete(self)

        return self

    def has_organisation(self, organisation_pid):
        """Check if record belongs to the organisation.

        :param str organisation_pid: Organisation PID
        :returns: True if record has organisation
        :rtype: Bool
        """
        for org in self.get('organisation', []):
            if organisation_pid == org['pid']:
                return True

        return False

    def has_subdivision(self, subdivision_pid):
        """Check if record belongs to the subdivision.

        :param str subdivision_pid: Subdivision PID
        :returns: True if record has subdivision
        :rtype: Bool
        """
        # No subdivision passed, means no check to do.
        if not subdivision_pid:
            return True

        # No subdivision in record, the document is accessible.
        if not self.get('subdivisions'):
            return False

        for subdivision in self['subdivisions']:
            if subdivision_pid == subdivision['pid']:
                return True

        # Subdivision not found, record is inaccessible
        return False


class SonarSearch(RecordsSearch):
    """Search Class SONAR."""

    class Meta:
        """Search only on item index."""

        index = 'records'


class SonarIndexer(RecordIndexer):
    """Indexing class for SONAR."""

    record_cls = SonarRecord

    def index(self, record):
        """Indexing a record.

        :param record: Record to index.
        :returns: Indexation result
        """
        return_value = super(SonarIndexer, self).index(record)

        index_name, doc_type = current_record_to_index(record)
        current_search.flush_and_refresh(index_name)
        return return_value

    def delete(self, record):
        """Delete a record.

        :param record: Record to remove from index.
        :returns: Indexation result
        """
        return_value = super(SonarIndexer, self).delete(record)
        index_name, doc_type = current_record_to_index(record)
        current_search.flush_and_refresh(index_name)
        return return_value
