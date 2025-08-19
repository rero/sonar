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
from random import randint

import click
from flask.cli import with_appcontext
from invenio_db import db
from rero_invenio_files.pdf import PDFGenerator

from sonar.modules.documents.cli.rerodoc import rerodoc
from sonar.modules.documents.cli.urn import urn
from sonar.modules.documents.serializers.schemas.dc import DublinCoreSchema

from ..api import DocumentIndexer, DocumentRecord


@click.group()
def documents():
    """Commands for documents."""


documents.add_command(rerodoc)
documents.add_command(urn)


@click.group("documents")
def documents_fixtures():
    """Commands to import documents."""


def extract_metadata(record):
    """Extract metadata from record."""
    dc = DublinCoreSchema()
    data = {}
    if title := dc.get_title(record):
        data["title"] = title
    if authors := dc.get_contributors(record):
        data["authors"] = authors
    if summary := dc.get_descriptions(record):
        data["summary"] = summary[0]["value"]
    return data


@documents_fixtures.command("import")
@click.argument("file", type=click.File("r"))
@click.option("-m", "--maximum", type=int, default=None, help="Maximum number of documents to import.")
@with_appcontext
def import_documents(file, maximum=None):
    """Import documents from JSON file."""
    click.secho(f"Importing document from {file.name}")

    indexer = DocumentIndexer()
    n = 0
    data_documents = json.load(file)
    if maximum is not None:
        data_documents = data_documents[:maximum]
    with click.progressbar(data_documents, label="Loading documents...") as bar:
        for record in bar:
            try:
                # Register record to DB
                db_record = DocumentRecord.create(record)
                data = extract_metadata({"metadata": db_record})
                for i in range(1, randint(2, 5)):
                    pdf = PDFGenerator(data)
                    pdf.render()
                    db_record.add_file(pdf.output(), f"document_{i}.pdf", label="Document", type="file")

                db_record.commit()
                db.session.commit()

                indexer.index(db_record)
                n += 1
            except Exception as error:
                click.secho(
                    f"Document {record} could not be imported: {error}",
                    fg="red",
                )

    click.secho(f"{n} documents imported.", fg="green")
