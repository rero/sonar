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
from io import BytesIO
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


def build_pids_by_org(pid_record_pairs, get_org_ref):
    """Build {org_pid: [pids]} from (pid, record) pairs."""
    mapping = {}
    for pid, record in pid_record_pairs:
        if record and (org_ref := get_org_ref(record)):
            mapping.setdefault(org_ref.split("/")[-1], []).append(pid)
    return mapping


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
        # Pre-build org → pids maps so random links stay within the same organisation.
        if doc_type == "doc":
            subdivision_pids_by_org = build_pids_by_org(
                ((pid, SubdivisionRecord.get_record_by_pid(pid)) for pid in SubdivisionRecord.get_all_pids()),
                lambda r: r.get("organisation", {}).get("$ref"),
            )
        if doc_type in ["doc", "depo"]:
            collections_pids_by_org = build_pids_by_org(
                ((pid, CollectionRecord.get_record_by_pid(pid)) for pid in CollectionRecord.get_all_pids()),
                lambda r: r.get("organisation", {}).get("$ref"),
            )
            project_service = current_app.extensions["sonar"].resources.get("projects").service
            # Projects use invenio-records-resources: PID → UUID → record (no get_record_by_pid).
            project_pids_by_org = build_pids_by_org(
                (
                    (p.pid_value, project_service.record_cls.get_record(str(p.object_uuid)))
                    for p in PersistentIdentifier.query.filter_by(pid_type=project_service.record_cls.pid_type)
                    .filter_by(status=PIDStatus.REGISTERED)
                    .all()
                ),
                lambda r: r.get("metadata", {}).get("organisation", {}).get("$ref"),
            )

    data_documents = json.load(file)
    with click.progressbar(data_documents, label="Loading record...") as bar:
        for record in bar:
            try:
                replace_user_from_dict(record)
                if service:
                    service.create(system_identity, record)
                else:
                    # Resolve the organisation PID for this record (used to scope random links below).
                    if doc_type == "doc":
                        org_refs = record.get("organisation", [])
                        org_pid = org_refs[0]["$ref"].split("/")[-1] if org_refs else None
                    elif doc_type == "depo":
                        # Deposits carry no direct org field; resolve it via the submitting user.
                        user_pid = record.get("user", {}).get("$ref", "").split("/")[-1]
                        user = UserRecord.get_record_by_pid(user_pid) if user_pid else None
                        org_pid = (
                            user["organisation"]["$ref"].split("/")[-1] if user and user.get("organisation") else None
                        )
                    else:
                        org_pid = None

                    # Randomly assign org-scoped links (1-in-11 chance each).
                    if (
                        doc_type == "doc"
                        and org_pid
                        and (org_subs := subdivision_pids_by_org.get(org_pid, []))
                        and random.randint(0, 10) == 0
                    ):
                        record["subdivisions"] = [
                            {"$ref": f"https://sonar.ch/api/subdivisions/{random.choice(org_subs)}"}
                        ]
                    if doc_type in ["doc", "depo"] and org_pid:
                        data = record["metadata"] if doc_type == "depo" else record
                        if (org_cols := collections_pids_by_org.get(org_pid, [])) and random.randint(0, 10) == 0:
                            data["collections"] = [
                                {"$ref": f"https://sonar.ch/api/collections/{random.choice(org_cols)}"}
                            ]
                        if (org_projs := project_pids_by_org.get(org_pid, [])) and random.randint(0, 10) == 0:
                            data["projects"] = [{"$ref": f"https://sonar.ch/api/projects/{random.choice(org_projs)}"}]

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
                                db_record.files[file["key"]] = BytesIO(f.read())
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
