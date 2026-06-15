# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""OAI harvester CLI commands."""

import json

import click
from click.exceptions import ClickException
from flask.cli import with_appcontext
from invenio_db import db
from invenio_oaiharvester.cli import oaiharvester
from invenio_oaiharvester.models import OAIHarvestConfig


@oaiharvester.group()
def config():
    """Configs commands for OAI harvesting."""


@config.command("create")
@click.argument("config_file", type=click.File("r"))
@with_appcontext
def oai_config_create(config_file):
    """Creates configurations for OAI harvesting.

    :param config_file: File containing a list of sources to harvest.
    """
    click.secho(f'\nCreating configurations for OAI harvesting from file "{config_file.name}"...')

    sources = json.load(config_file)

    if not sources or not isinstance(sources, list):
        raise ClickException("Configurations file cannot be parsed")

    for source in sources:
        try:
            configuration = OAIHarvestConfig.query.filter_by(name=source["key"]).first()

            if configuration:
                raise Exception(f'Config already registered for "{source["key"]}"')

            configuration = OAIHarvestConfig(
                name=source["key"],
                baseurl=source["url"],
                metadataprefix=source["metadataprefix"],
                setspecs=source["setspecs"],
                comment=source["comment"],
            )
            configuration.save()
            db.session.commit()

            click.secho(
                f'Created configuration for "{source["key"]}"',
                fg="green",
            )
        except Exception as exception:
            click.secho(str(exception), fg="yellow")

    click.secho("Done", fg="green")


@config.command("list")
@with_appcontext
def oai_config_info():
    """List infos for tasks."""
    oais = OAIHarvestConfig.query.all()
    for oai in oais:
        click.secho("\n" + oai.name, underline=True)
        click.echo("\tlastrun       : ", nl=False)
        click.echo(oai.lastrun)
        click.echo("\tbaseurl       : " + oai.baseurl)
        click.echo("\tmetadataprefix: " + oai.metadataprefix)
        click.echo("\tcomment       : " + oai.comment)
        click.echo("\tsetspecs      : " + oai.setspecs)
