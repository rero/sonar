# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2019 RERO
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

"""OAI harvester CLI commands."""

import json

import click
from click.exceptions import ClickException
from flask import current_app
from flask.cli import with_appcontext
from invenio_db import db
from invenio_oaiharvester.cli import harvest, oaiharvester
from invenio_oaiharvester.models import OAIHarvestConfig


@oaiharvester.group()
def config():
    """Configs commands for OAI harvesting."""


@config.command('create')
@click.argument('config_file', type=click.File('r'))
@with_appcontext
def oai_config_create(config_file):
    """Creates configurations for OAI harvesting.

    :param config_file: File containing a list of sources to harvest.
    """
    click.secho(
        '\nCreating configurations for OAI harvesting from file "{file}"...'.
        format(file=config_file.name))

    sources = json.load(config_file)

    if not sources or not isinstance(sources, list):
        raise ClickException('Configurations file cannot be parsed')

    for source in sources:
        try:
            configuration = OAIHarvestConfig.query.filter_by(
                name=source['key']).first()

            if configuration:
                raise Exception(
                    'Config already registered for "{name}"'.format(
                        name=source['key']))

            configuration = OAIHarvestConfig(
                name=source['key'],
                baseurl=source['url'],
                metadataprefix=source['metadataprefix'],
                setspecs=source['setspecs'],
                comment=source['comment'])
            configuration.save()
            db.session.commit()

            click.secho('Created configuration for "{name}"'.format(
                name=source['key']),
                        fg='green')
        except Exception as exception:
            click.secho(str(exception), fg='yellow')

    click.secho('Done', fg='green')


@config.command('list')
@with_appcontext
def oai_config_info():
    """List infos for tasks."""
    oais = OAIHarvestConfig.query.all()
    for oai in oais:
        click.secho('\n' + oai.name, underline=True)
        click.echo('\tlastrun       : ', nl=False)
        click.echo(oai.lastrun)
        click.echo('\tbaseurl       : ' + oai.baseurl)
        click.echo('\tmetadataprefix: ' + oai.metadataprefix)
        click.echo('\tcomment       : ' + oai.comment)
        click.echo('\tsetspecs      : ' + oai.setspecs)


@oaiharvester.command('harvest-all')
@click.option('-m',
              '--max',
              type=int,
              default=None,
              help='Maximum of records to harvest (optional).')
@click.option('-k',
              '--enqueue',
              is_flag=True,
              default=False,
              help="Enqueue harvesting and return immediately.")
@click.option(
    '-f',
    '--force',
    is_flag=True,
    default=False,
    help='Force to re-import records, (don\'t take care of last run date).'
)
@with_appcontext
@click.pass_context
def oai_config_harvest_all(ctx, max, enqueue, force):
    """Harvesting data for the set and the configuration.

    :param ctx: App context.
    :param max: Max records to harvest for each sources.
    :param enqueue: Enqueue process or return immediately.
    :param force: Force to re-import records.
    """
    with current_app.app_context():
        sources = OAIHarvestConfig.query.all()

    arguments = []

    if max:
        arguments.append('max={max}'.format(max=max))

    for source in sources:
        name = source.name
        ctx.invoke(harvest,
                   name=name,
                   arguments=arguments,
                   enqueue=enqueue,
                   quiet=True,
                   from_date='1900-01-01' if force else None)
