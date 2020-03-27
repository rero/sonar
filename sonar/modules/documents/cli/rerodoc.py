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

"""RERODOC specific CLI commands."""

import csv
import re

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_db import db
from invenio_indexer.api import RecordIndexer

from sonar.modules.documents.api import DocumentRecord


@click.group()
def rerodoc():
    """RERODOC specific commands."""


@rerodoc.command('update-file-permissions')
@click.argument('permissions_file', type=click.File('r'))
@click.option('-c',
              '--chunk-size',
              type=int,
              default=500,
              help='Chunk size for bulk indexing.')
@with_appcontext
def update_file_permissions(permissions_file, chunk_size):
    """Update file permission with information given by input file.

    :param permissions_file: CSV file containing files permissions.
    """
    indexer = RecordIndexer()

    def save_records(ids):
        """Save current records set into database and re-index.

        :param ids: List of records to save
        """
        db.session.commit()
        indexer.bulk_index(ids)
        indexer.process_bulk_queue()

    click.secho(permissions_file.name)
    try:
        with open(permissions_file.name, 'r') as file:
            reader = csv.reader(file, delimiter=';')

            # header
            header = next(reader)

            # check number of columns
            if len(header) != 3:
                raise Exception('CSV file seems to be not well formatted.')

            # To store ids for bulk indexing
            ids = []

            for row in reader:
                try:
                    # try to load corresponding record
                    record = DocumentRecord.get_record_by_identifier([{
                        'type':
                        'bf:Local',
                        'value':
                        row[0]
                    }])

                    # No record found, skipping..
                    if not record:
                        raise Exception(
                            'Record {record} not found'.format(record=row[0]))

                    file_name = '{key}.pdf'.format(key=row[2])

                    # File not found in record, skipping
                    if file_name not in record.files:
                        raise Exception(
                            'File {file} not found in record {record}'.format(
                                file=file_name, record=row[0]))

                    record_file = record.files[file_name]

                    # permissions contains a status
                    matches = re.search(r'status:(\w+)$', row[1])
                    if matches:
                        # If status if RERO or INTERNAL, file must not be
                        # displayed, otherwise file is restricted within
                        # institution
                        if matches.group(1) in ['RERO', 'INTERNAL']:
                            current_app.logger.warning(
                                'Access restricted to {status} for file '
                                '{record}'.format(status=matches.group(1),
                                                  record=row))
                            record_file['restricted'] = matches.group(
                                1).lower()
                        else:
                            record_file['restricted'] = 'institution'
                    else:
                        # permissions contains a date
                        matches = re.search(
                            r'allow roles \/\.\*,(\w+),\.\*\/\n\s+.+(\d{4}-'
                            r'\d{2}-\d{2})', row[1])

                        if matches:
                            # file is restricted to institution
                            if matches.group(1) != 'INTERNAL':
                                record_file['restricted'] = 'institution'

                            record_file['embargo_date'] = matches.group(2)

                    record.commit()
                    db.session.flush()
                    ids.append(str(record.id))

                    # Bulk save and index
                    if len(ids) % chunk_size == 0:
                        save_records(ids)
                        ids = []

                except Exception as exception:
                    click.secho(str(exception), fg='yellow')

        # save remaining records
        save_records(ids)

        click.secho('Process finished', fg='green')

    except Exception as exception:
        click.secho('An error occured during file process: {error}'.format(
            error=str(exception)),
                    fg='red')
