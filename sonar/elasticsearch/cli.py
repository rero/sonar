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

"""CLI for Elasticsearch."""

import datetime

import click
from flask.cli import with_appcontext
from invenio_search import current_search_client


def abort_if_false(ctx, param, value):
    """Abort command is value is False."""
    if not value:
        ctx.abort()


@click.group()
def es():
    """Commands for ES."""


@click.group()
def snapshot():
    """Snapshot commands."""


@click.command()
@click.option("--repository", "repository", default="backup")
@with_appcontext
def create_repository(repository):
    """Create repository for snapshot.

    :param repository: Repository name.
    """
    click.secho("Create a repository for snapshots")

    try:
        current_search_client.snapshot.create_repository(
            repository, {"type": "fs", "settings": {"location": repository}}
        )
        click.secho("Done", fg="green")
    except Exception as exception:
        click.secho(str(exception), fg="red")


@click.command()
@click.option("--repository", "repository", default="backup")
@click.option("--name", "name")
@click.option("--wait/--no-wait", default=False)
@with_appcontext
def backup(repository, name, wait):
    """Backup elasticsearch data.

    :param repository: Repository name.
    :param name: Name of the snapshot.
    :param wait: Wait for completion.
    """
    click.secho("Backup elasticsearch data")

    # If no name, create a snapshot with the current date
    if not name:
        name = "snapshot-{date}".format(date=datetime.date.today().strftime("%Y-%m-%d"))

        click.secho("Create a snapshot with name {name}".format(name=name))

    try:
        # Remove old backup with the same name
        try:
            current_search_client.snapshot.delete(repository, name)
        except Exception:
            pass

        # Backup data
        current_search_client.snapshot.create(
            repository, name, wait_for_completion=wait
        )

        click.secho("Done", fg="green")
    except Exception as exception:
        click.secho(str(exception), fg="red")


@click.command()
@click.option("--repository", "repository", default="backup")
@click.option("--name", "name", required=True)
@click.option("--wait/--no-wait", default=False)
@click.option(
    "--yes-i-know",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Do you really want to restore a snapshot?",
)
@with_appcontext
def restore(repository, name, wait):
    """Restore elasticsearch data.

    :param repository: Repository name.
    :param name: Name of the snapshot.
    :param wait: Wait for completion.
    """
    click.secho("Restore elasticsearch data")
    try:
        # Remove all indices
        current_search_client.indices.delete("_all")

        # Restore the snapshot
        current_search_client.snapshot.restore(
            repository, name, wait_for_completion=wait
        )

        click.secho("Done", fg="green")
    except Exception as exception:
        click.secho(str(exception), fg="red")


snapshot.add_command(create_repository)
snapshot.add_command(backup)
snapshot.add_command(restore)
es.add_command(snapshot)
