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

import time

from dojson.contrib.marc21.utils import create_record

from .api import DocumentRecord
from .dojson.contrib.marc21tojson.model import marc21tojson
from .tasks import import_records

CHUNK_SIZE = 100


def transform_harvested_records(sender=None, records=None, **kwargs):
    """Harvest records and transform them and send to the import queue.

    This function is called when the oaiharvester command is finished.

    :param sender: Sender of the signal.
    :param list records: Liste of records to harvest.
    """
    start_time = time.time()

    max_records = kwargs.get('max', None)

    if kwargs.get('name'):
        print('Harvesting records from "{set}"'.format(set=kwargs.get('name')))

    harvested_records = list(records)

    # Reduce array to max records
    if max_records:
        harvested_records = harvested_records[:int(max_records)]

    records = []

    for harvested_record in harvested_records:
        # Convert from Marc XML to JSON
        data = create_record(harvested_record.xml)

        # Transform JSON
        data = marc21tojson.do(data)

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
        if file['type'] == 'fulltext':
            with file.file.storage().open() as pdf_file:
                json['fulltext'].append(pdf_file.read().decode('utf-8'))


def chunks(records, size):
    """Yield chunks from records.

    :param list records: Full records list.
    :param int size: Size of chunks.
    """
    for i in range(0, len(records), size):
        yield records[i:i + size]
