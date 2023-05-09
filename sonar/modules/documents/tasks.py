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

"""Tasks for document in celery."""

from celery import shared_task
from flask import current_app
from invenio_db import db
from invenio_indexer.api import RecordIndexer


@shared_task(ignore_result=True)
def import_records(records_to_import):
    """Import records in database and index them.

    Used as celery task. "ignore_result" flag means that we don't want to
    get the status and/or the result of the task, execution is faster.

    :param list records_to_import: List of records to import.
    :returns: List of IDs.
    """
    from sonar.modules.documents.api import DocumentRecord
    indexer = RecordIndexer()

    ids = []

    for data in records_to_import:
        try:
            files_data = data.pop('files', [])

            record = DocumentRecord.get_record_by_identifier(
                data.get('identifiedBy', []))

            # Set record as harvested
            data['harvested'] = True

            if not record:
                record = DocumentRecord.create(data,
                                               dbcommit=False,
                                               with_bucket=True)
            else:
                current_app.logger.warning(
                    'Record already imported with PID {pid}: {record}'.format(
                        pid=record['pid'], record=data))
                record.update(data)

            for file_data in files_data:
                # Store url and key and remove it from dict to pass dict to
                # kwargs in add_file_from_url method
                url = file_data.pop('url')
                key = file_data.pop('key')

                try:
                    if url.startswith('http'):
                        record.add_file_from_url(url, key, **file_data)
                    else:
                        with open(url, 'rb') as pdf_file:
                            record.add_file(pdf_file.read(), key,
                                            **file_data)
                except Exception as exception:
                    current_app.logger.warning(
                        'Error during import of file {file} of record '
                        '{record}: {error}'.format(
                            file=key,
                            error=exception,
                            record=record['identifiedBy']))

            # Merge record in database, at this time it's not saved into DB.
            record.commit()

            # Pushing record to database, not yet persisted into DB
            db.session.flush()

            # Add ID for bulk index in elasticsearch
            ids.append(str(record.id))

            current_app.logger.info(
                'Record with reference "{reference}" imported successfully'.
                format(reference=record['identifiedBy']))

        except Exception as exception:
            current_app.logger.error(
                'Error during importation of record {record}: {exception}'.
                format(record=data, exception=exception))

    # Commit and index records
    db.session.commit()
    indexer.bulk_index(ids)
    indexer.process_bulk_queue()

    return ids
