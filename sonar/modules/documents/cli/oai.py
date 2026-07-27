# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""OAI specific CLI commands."""

import click
from flask.cli import with_appcontext
from invenio_db import db
from invenio_oaiserver.models import OAISet


@click.group()
def oai():
    """URN specific commands."""


@oai.command()
@click.argument("code")
@click.argument("name")
@click.argument("pattern")
@with_appcontext
def create_set(code, name, pattern):
    """Create an OAI set."""
    oaiset = OAISet(
        spec=code,
        name=name,
        search_pattern=pattern,
        system_created=True,
    )
    db.session.add(oaiset)
    db.session.commit()
    click.secho(f"OAI set '{code}' created.", fg="green")
    click.secho("Please reindex existing documents if needed.", fg="yellow")
