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

"""ARK CLI commands."""

import click
from elasticsearch_dsl import Q
from flask.cli import with_appcontext
from invenio_db import db

from sonar.modules.documents.api import DocumentRecord, DocumentSearch
from sonar.modules.organisations.api import OrganisationRecord

from .api import Ark


@click.group()
@with_appcontext
def ark():
    """ARK utils commands."""
    if not Ark():
        click.secho("ARK is not enabled.", fg="red")
        raise click.Abort()


@ark.command()
@with_appcontext
def config():
    """Dump the ARK client configurations."""
    click.secho(f"{Ark().config()}")


@ark.command()
@click.argument("organisation_pid")
@with_appcontext
def create_missing(organisation_pid):
    """Create an ark identifier in the document of the given organisation."""
    organisation = OrganisationRecord.get_record_by_pid(organisation_pid)
    if not organisation:
        click.secho("Organisation does not exist.", fg="red")
        raise click.Abort()
    if not organisation.get("arkNAAN"):
        click.secho(
            "NAAN configuration does not exist for the given organisation.", fg="red"
        )
        raise click.Abort()
    search = (
        DocumentSearch()
        .source("pid")
        .filter(
            "bool",
            must_not=[
                Q(
                    "nested",
                    path="identifiedBy",
                    query=Q("term", identifiedBy__type="ark"),
                ),
                Q("term", harvested=True),
            ],
        )
        .filter("term", organisation__pid=organisation_pid)
    )

    if not search.count():
        click.secho("No document found.", fg="yellow")
        raise click.Abort()

    ark = Ark(naan=organisation.get("arkNAAN"))
    if not ark:
        click.secho("Ark is not enabled.", fg="red")
        raise click.Abort()

    click.secho(f"Detected {search.count()}", fg="green")
    n = 0
    with click.progressbar(search.scan()) as bar:
        for res in bar:
            doc = DocumentRecord.get_record_by_pid(res.pid)
            pid = ark.create(doc["pid"], record_uuid=doc.id)
            assert not doc.get_ark()
            doc.setdefault("identifiedBy", []).append(
                dict(type="ark", value=pid.pid_value)
            )
            doc.commit()
            db.session.commit()
            doc.reindex()
            n += 1
    click.secho(f"{n} document has been updated.", fg="green")
