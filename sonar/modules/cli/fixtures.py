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

"""Fixtures commands."""

import json
import os
import random
from random import randint

import click
from click import ClickException
from flask import current_app
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_base.utils import obj_or_import_string
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from rero_invenio_files.pdf import PDFGenerator

from sonar.modules.collections.api import Record as CollectionRecord
from sonar.modules.documents.serializers.schemas.dc import DublinCoreSchema
from sonar.modules.subdivisions.api import Record as SubdivisionRecord
from sonar.modules.users.api import UserRecord

from ..users.cli import users


@click.group()
def fixtures():
    """Fixtures commands."""


def extract_metadata(record):
    """Extract metadata from record.

    Extract title, authors and summary from record using DublinCoreSchema.

    :param record: The record to extract data from.
    """
    dc = DublinCoreSchema()
    data = {}
    if title := dc.get_title(record):
        data["title"] = title
    if authors := dc.get_contributors(record):
        data["authors"] = authors
    if summary := dc.get_descriptions(record):
        data["summary"] = summary[0]["value"]
    return data


def replace_user_from_dict(a_dict):
    """Replace a user email by a $ref from a multi level dictionary.

    :param a_dict: The dictionary to parse.
    """
    if not isinstance(a_dict, dict):
        return
    for k, v in a_dict.items():
        if k == "user" and isinstance(v, str):
            pid = UserRecord.get_pid_by_email(v)
            a_dict[k] = {"$ref": f"https://sonar.ch/api/users/{pid}"}
        if isinstance(v, dict):
            v = replace_user_from_dict(v)
        elif isinstance(v, list):
            v = [replace_user_from_dict(el) for el in v if el]


@fixtures.command("import")
@click.argument("file", type=click.File("r"))
@click.argument("doc_type")
@click.option("--random-files", "-r", is_flag=True, help="Print more output.")
@click.option("--with-file-support", "-f", is_flag=True, help="Add file support.")
@with_appcontext
def import_data(file, doc_type, random_files, with_file_support):
    """Import organisations from JSON file."""
    click.secho(f"Importing {doc_type} from {file.name}")

    directory = os.path.dirname(file.name)

    config = current_app.config.get("RECORDS_REST_ENDPOINTS", {}).get(doc_type)
    service = None
    indexer = None
    record_class = None
    if not config:
        resource = current_app.extensions["sonar"].resources.get(doc_type)
        if not resource:
            raise ClickException(f"Document type '{doc_type}' not found.")
        service = resource.service
    else:
        indexer = obj_or_import_string(config.get("indexer_class"))()
        record_class = obj_or_import_string(config.get("record_class"))
        if doc_type == "doc":
            subdivision_pids = list(SubdivisionRecord.get_all_pids())
        if doc_type in ["doc", "depo"]:
            collections_pids = list(CollectionRecord.get_all_pids())
            project_service = current_app.extensions["sonar"].resources.get("projects").service
            project_pids = [
                r.pid_value
                for r in PersistentIdentifier.query.filter_by(pid_type=project_service.record_cls.pid_type)
                .filter_by(status=PIDStatus.REGISTERED)
                .all()
            ]

    data_documents = json.load(file)
    with click.progressbar(data_documents, label="Loading record...") as bar:
        for record in bar:
            try:
                replace_user_from_dict(record)
                if service:
                    service.create(system_identity, record)
                else:
                    # create random links to subdivisions, collections and projects
                    if doc_type == "doc" and random.randint(0, 10) == 0:
                        record["subdivisions"] = [
                            {"$ref": f"https://sonar.ch/api/subdivisions/{random.choice(subdivision_pids)}"}
                        ]
                    if doc_type in ["doc", "depo"]:
                        data = record
                        if doc_type == "depo":
                            data = record["metadata"]
                        if random.randint(0, 10) == 0:
                            data["collections"] = [
                                {"$ref": f"https://sonar.ch/api/collections/{random.choice(collections_pids)}"}
                            ]
                        if random.randint(0, 10) == 0:
                            data["projects"] = [
                                {"$ref": f"https://sonar.ch/api/projects/{random.choice(project_pids)}"}
                            ]

                    files = record.pop("files", [])
                    if not with_file_support and (files or random_files):
                        raise ClickException("Files found in record but file support is not activated. Use -f option.")
                    # Register record to DB
                    db_record = record_class.create(data=record, with_bucket=with_file_support)
                    # Add files
                    for file in files:
                        file_path = os.path.join(directory, file["path"])
                        if os.path.isfile(file_path):
                            with open(file_path, "rb") as f:
                                db_record.add_file(f.read(), file["key"])
                    if random_files:
                        data = extract_metadata({"metadata": db_record})
                        for i in range(1, randint(2, 5)):
                            pdf = PDFGenerator(data)
                            pdf.render()
                            db_record.add_file(pdf.output(), f"document_{i}.pdf", label="Document", type="file")
                    db_record.commit()
                    db.session.commit()

                    indexer.index(db_record)
            except Exception as error:
                click.secho(
                    f"Record {record} could not be imported: {error}",
                    fg="red",
                )
    click.secho("Finished", fg="green")


fixtures.add_command(users)
