# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Resources CLI commands."""

import click
from flask.cli import with_appcontext
from invenio_indexer.cli import abort_if_false

from sonar.proxies import sonar


@click.group()
def resources():
    """Resources CLI commands."""


@resources.command("reindex")
@click.argument("record-type")
@click.option(
    "--yes-i-know",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Do you really want to reindex all records?",
)
@with_appcontext
def reindex(record_type):
    """Reindex all records for the given type.

    Reindex all records managed by `invenio-records-resouces` for the given
    type.

    :param record_type: Record type.
    """
    click.secho(f'Indexing records of type "{record_type}"')
    sonar.service(record_type).bulk_reindex()
    click.secho("Record indexed successfully!", fg="green")
