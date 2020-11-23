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

"""Deposit CLI commands."""

import shutil
from os import makedirs
from os.path import exists, join

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_db import db
from invenio_files_rest.models import Bucket, FileInstance, Location, \
    ObjectVersion


@click.group()
def deposits():
    """Deposits CLI commands."""


@deposits.command('create')
@with_appcontext
def create():
    """Create a location and a bucket for uploading files."""
    click.secho('Creating default location for importing files', bold=True)

    # Directory where files are stored
    directory = current_app.config.get('SONAR_APP_STORAGE_PATH')
    if not directory:
        directory = current_app.instance_path
    directory = join(directory, 'files')

    if exists(directory):
        shutil.rmtree(directory)

    makedirs(directory)

    # Remove stored data
    ObjectVersion.query.delete()
    Bucket.query.delete()
    FileInstance.query.delete()
    Location.query.delete()
    db.session.commit()

    # Create location
    loc = Location(name='local', uri=directory, default=True)
    db.session.add(loc)
    db.session.commit()

    click.secho('Location #{id} created successfully'.format(id=loc.id),
                fg='green')
