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

"""HEG record harvester."""

import datetime
import json
from os import listdir, path, remove

import click
from flask import current_app
from flask.cli import with_appcontext

from sonar.heg.ftp import HEGRepository
from sonar.heg.record import HEGRecord
from sonar.modules.documents.tasks import \
    import_records as document_import_records
from sonar.modules.utils import chunks

CHUNK_SIZE = 100


@click.group()
def harvest():
    """Commands for harvesting records from HEG."""


@harvest.command()
@click.option('--file', 'file')
@with_appcontext
def queue_files(file):
    """Queue files retrieved from HEG repository.

    param file: File to download
    """
    # If file is not set, the file is guessed from current date
    if not file:
        file = 'data_{date}.zip'.format(
            date=datetime.date.today().strftime('%d%m%y'))

    click.secho('Queue files from file "{file}"'.format(file=file))

    try:
        heg_repository = HEGRepository('candy.hesge.ch', 'SONAR/production')
        heg_repository.connect()
        heg_repository.queue_files(
            file, current_app.config.get('SONAR_APP_HEG_DATA_DIRECTORY'))

        click.secho('Files queued successfully', fg='green')
    except Exception as exception:
        click.secho(str(exception), fg='red')


@harvest.command()
@click.option('--file', 'file', multiple=True)
@click.option('--remove-file', is_flag=True, default=False)
@with_appcontext
def import_records(file, remove_file):
    """Import records from HEG.

    :param file: Specific files to import, if not set, all the files in the
    folder will be imported.
    :param remove_file: If True, remove file after process.
    """
    target_directory = current_app.config.get('SONAR_APP_HEG_DATA_DIRECTORY')

    if not file:
        file = [
            f for f in listdir(target_directory) if f.startswith('HEG_data')
        ]

    for single_file in file:
        records = []

        try:
            file_path = path.join(target_directory, single_file)

            with open(file_path, 'r') as json_file:
                for data in json_file.readlines():
                    data = json.loads(data)
                    try:
                        heg_record = HEGRecord(data)
                        records.append(heg_record.serialize())
                    except Exception as exception:
                        click.secho('Error during processing record {record}: '
                                    '{exception}'.format(record=data,
                                                         exception=exception),
                                    fg='red')

            # Chunk record list and send celery task
            for chunk in list(chunks(records, CHUNK_SIZE)):
                document_import_records.delay(chunk)

            if remove_file:
                remove(file_path)

            click.secho(
                'Process finished for file "{file}", the data will be '
                'imported in background'
                .format(file=file_path),
                fg='green')
        except Exception as exception:
            click.secho(str(exception), fg='red')
