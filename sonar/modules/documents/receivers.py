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

"""Signals connections for documents."""

import json
import time
from datetime import datetime
from os import makedirs
from os.path import exists, join

import pytz
from flask import current_app

from sonar.modules.api import SonarRecord
from sonar.modules.documents.api import DocumentRecord
from sonar.modules.documents.loaders.schemas.factory import LoaderSchemaFactory
from sonar.webdav import HegClient

from .api import DocumentRecord
from .tasks import import_records

CHUNK_SIZE = 100


def transform_harvested_records(sender=None, records=None, **kwargs):
    """Harvest records and transform them and send to the import queue.

    This function is called when the oaiharvester command is finished.

    :param sender: Sender of the signal.
    :param list records: Liste of records to harvest.
    """
    if kwargs.get('action', 'import') != 'import':
        return

    start_time = time.time()

    max_records = kwargs.get('max', None)
    # Cancel parameter if max is set to 0
    if max_records == '0':
        max_records = None

    if kwargs.get('name'):
        print('Harvesting records from "{set}"'.format(set=kwargs.get('name')))

    harvested_records = list(records)

    # Reduce array to max records
    if max_records:
        harvested_records = harvested_records[:int(max_records)]

    records = []

    loader_schema = LoaderSchemaFactory.create(kwargs['name'])

    for harvested_record in harvested_records:
        # Convert from Marc XML to JSON
        data = loader_schema.dump(str(harvested_record))

        # Add transformed data to list
        records.append(data)

    # Chunk record list and send celery task
    for chunk in list(chunks(records, CHUNK_SIZE)):
        import_records.delay(chunk)

    print('{count} records harvested in {time} seconds'.format(
        count=len(records), time=time.time() - start_time))


def populate_fulltext_field(sender=None,
                            record=None,
                            json=None,
                            index=None,
                            **kwargs):
    """Receive a signal before record is indexed, to add fulltext.

    This function is called just before a record is sent to index.

    :param sender: Sender of the signal.
    :param Record record: Record to index.
    :param dict json: JSON that will be indexed.
    :param str index: Name of the index in which record will be sent.
    """
    # Takes care only about documents indexing
    if not index.startswith('documents'):
        return

    # Transform record in DocumentRecord
    if not isinstance(record, DocumentRecord):
        record = DocumentRecord.get_record(record.id)

    # No files are present in record
    if not record.files:
        return

    # Store fulltext in array for indexing
    json['fulltext'] = []
    for file in record.files:
        if file.get('type') == 'fulltext':
            with file.file.storage().open() as pdf_file:
                json['fulltext'].append(pdf_file.read().decode('utf-8'))


def chunks(records, size):
    """Yield chunks from records.

    :param list records: Full records list.
    :param int size: Size of chunks.
    """
    for i in range(0, len(records), size):
        yield records[i:i + size]


def update_oai_property(sender, record):
    """Called when a document is created or updated.

    Update `_oai` property of the record.

    :param sender: Sender
    :param record: Document record
    """
    if not isinstance(record, DocumentRecord):
        return

    record['_oai']['updated'] = pytz.utc.localize(
        datetime.utcnow()).isoformat()
    record['_oai']['sets'] = [
        SonarRecord.get_pid_by_ref_link(record['organisation']['$ref'])
    ] if record.get('organisation') else []


def export_json(sender=None, records=None, **kwargs):
    """Export records in JSON and store them in a file.

    :param sender: Sender of the signal.
    :param records: List of records to harvest.
    """
    if not kwargs.get('name') or kwargs.get('action') != 'export':
        return

    data_directory = current_app.config.get('SONAR_APP_STORAGE_PATH')
    if not data_directory:
        data_directory = current_app.instance_path
    data_directory = join(data_directory, 'data')

    if not exists(data_directory):
        makedirs(data_directory)

    records_to_export = []

    print('{count} records harvested'.format(count=len(records)))

    for record in records:
        loader_schema = LoaderSchemaFactory.create(kwargs['name'])
        records_to_export.append(loader_schema.dump(str(record)))

    file_name = '{source}-{date}.json'.format(
        source=kwargs['name'], date=datetime.now().strftime('%Y%m%d%H%M%S'))
    file_path = join(data_directory, file_name)

    json_file = open(file_path, 'w')
    json_file.write(json.dumps(records_to_export))

    # Export to webdav for HEG
    client = HegClient()
    client.upload_file(file_name, file_path)

    print('{count} records exported'.format(count=len(records_to_export)))
