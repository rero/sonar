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

"""Documents CLI commands."""

import json
from functools import partial

import click
import requests
from click.exceptions import ClickException
from flask import current_app
from flask.cli import with_appcontext
from invenio_db import db
from invenio_indexer.api import RecordIndexer

from .api import InstitutionRecord


@click.group()
def institutions():
    """Institutions CLI commands."""


@institutions.command('import')
@with_appcontext
def import_institutions():
    """Import institutions from JSON file."""
    institution_file = './data/institutions.json'
    click.secho('Importing institution from {file}'.format(
        file=institution_file))

    indexer = RecordIndexer()

    with open(institution_file) as json_file:
        records = json.load(json_file)
        for record in records:
            try:
                # Check existence in DB
                db_record = InstitutionRecord.get_record_by_pid(record['pid'])

                if db_record:
                    raise ClickException('Record already exists in DB')

                # Register record to DB
                db_record = InstitutionRecord.create(record)
                db.session.commit()

                indexer.index(db_record)
            except Exception as error:
                click.secho(
                    'Institution {institution} could not be imported: {error}'
                    .format(institution=record, error=str(error)), fg='red')

    click.secho('Finished', fg='green')
