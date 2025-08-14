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

"""RERODOC specific CLI commands."""

import csv
import re

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_db import db

from sonar.modules.documents.api import DocumentIndexer, DocumentRecord


@click.group()
def rerodoc():
    """RERODOC specific commands."""


@rerodoc.command("update-file-permissions")
@click.argument("permissions_file", type=click.File("r"))
@click.option(
    "-c", "--chunk-size", type=int, default=500, help="Chunk size for bulk indexing."
)
@with_appcontext
def update_file_permissions(permissions_file, chunk_size):
    """Update file permission with information given by input file.

    :param permissions_file: CSV file containing files permissions.
    """
    indexer = DocumentIndexer(record_cls=DocumentRecord)

    def save_records(ids):
        """Save current records set into database and re-index.

        :param ids: List of records to save
        """
        db.session.commit()
        indexer.bulk_index(ids)
        indexer.process_bulk_queue()

    try:
        with open(permissions_file.name, "r") as file:
            reader = csv.reader(file, delimiter=",")

            # header
            header = next(reader)

            # check number of columns
            if len(header) != 3:
                raise Exception("CSV file seems to be not well formatted.")

            # To store ids for bulk indexing
            ids = []

            for row in reader:
                try:
                    # try to load corresponding record
                    record = DocumentRecord.get_record_by_identifier(
                        [{"type": "bf:Local", "value": row[0]}]
                    )

                    # No record found, skipping..
                    if not record:
                        raise Exception(f"Record {row[0]} not found")

                    file_name = f"{row[2]}.pdf"

                    # File not found in record, skipping
                    if file_name not in record.files:
                        raise Exception(
                            f"File {file_name} not found in record {row[0]}"
                        )

                    record_file = record.files[file_name]

                    # permissions contains a status
                    matches = re.search(r"status:(\w+)$", row[1])
                    if matches:
                        # If status if RERO or INTERNAL, file must not be
                        # displayed, otherwise file is not accessible outside
                        # organisation
                        record_file["access"] = "coar:c_16ec"  # restricted access
                        if matches.group(1) in ["RERO", "INTERNAL"]:
                            record_file["restricted_outside_organisation"] = False
                        else:
                            record_file["restricted_outside_organisation"] = True
                    else:
                        # permissions contains a date
                        matches = re.search(
                            r"allow roles \/\.\*,(\w+),\.\*\/\n\s+.+(\d{4}-"
                            r"\d{2}-\d{2})",
                            row[1],
                        )

                        if matches:
                            # file is accessible inside organisation
                            if matches.group(1) != "INTERNAL":
                                record_file["restricted_outside_organisation"] = True
                            # file is not accessible
                            else:
                                record_file["restricted_outside_organisation"] = False

                            record_file["access"] = "coar:c_f1cf"  # embargoed access
                            record_file["embargo_date"] = matches.group(2)

                    record.commit()
                    db.session.flush()
                    ids.append(str(record.id))

                    current_app.logger.warning(
                        f"Restriction added for file {file_name} in record {record['pid']}."
                    )

                    # Bulk save and index
                    if len(ids) % chunk_size == 0:
                        save_records(ids)
                        ids = []

                except Exception as exception:
                    click.secho(str(exception), fg="yellow")

        # save remaining records
        save_records(ids)

        click.secho("Process finished", fg="green")

    except Exception as exception:
        click.secho(
            f"An error occured during file process: {exception}",
            fg="red",
        )
