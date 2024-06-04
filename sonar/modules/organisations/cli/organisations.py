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

"""Documents CLI commands."""

import json
import os.path
from io import BytesIO

import click
from click.exceptions import ClickException
from flask.cli import with_appcontext
from invenio_db import db

from sonar.modules.organisations.api import OrganisationIndexer, OrganisationRecord


@click.group()
def organisations():
    """Organisations CLI commands."""


@organisations.command("import")
@click.argument("file", type=click.File("r"))
@with_appcontext
def import_organisations(file):
    """Import organisations from JSON file."""
    click.secho("Importing organisations from {file}".format(file=file.name))

    directory = os.path.dirname(file.name)

    indexer = OrganisationIndexer()

    for record in json.load(file):
        try:
            # Check existence in DB
            db_record = OrganisationRecord.get_record_by_pid(record["code"])

            if db_record:
                raise ClickException("Record already exists in DB")

            files = record.pop("files", [])

            # Register record to DB
            db_record = OrganisationRecord.create(record)

            # Add files
            for file in files:
                file_path = os.path.join(directory, file["path"])
                if os.path.isfile(file_path):
                    with open(file_path, "rb") as f:
                        db_record.files[file["key"]] = BytesIO(f.read())

            db_record.commit()
            db.session.commit()

            indexer.index(db_record)
        except Exception as error:
            click.secho(
                "Organisation {org} could not be imported: {error}".format(
                    org=record, error=str(error)
                ),
                fg="red",
            )

    click.secho("Finished", fg="green")
