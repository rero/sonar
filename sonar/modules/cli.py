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

"""SONAR CLI commands."""

import json
import sys

import click
import jsonref
from flask.cli import with_appcontext
from invenio_search.cli import es_version_check
from invenio_search.proxies import current_search

from .deposits.cli import deposits
from .users.cli import users


@click.group()
def fixtures():
    """Fixtures management commands."""


fixtures.add_command(users)
fixtures.add_command(deposits)


@click.group()
def utils():
    """Utils commands."""


@utils.command()
@click.option('--force', is_flag=True, default=False)
@with_appcontext
@es_version_check
def es_init(force):
    """Initialize registered templates, aliases and mappings."""
    # TODO: to remove once it is fixed in invenio-search module
    click.secho('Putting templates...', fg='green', bold=True, file=sys.stderr)
    with click.progressbar(
            current_search.put_templates(ignore=[400] if force else None),
            length=len(current_search.templates)) as item:
        for response in item:
            item.label = response
    click.secho('Creating indexes...', fg='green', bold=True, file=sys.stderr)
    with click.progressbar(
            current_search.create(ignore=[400] if force else None),
            length=len(current_search.mappings)) as item:
        for name, response in item:
            item.label = name


@utils.command()
@click.argument('src_json_file', type=click.File('r'))
@click.option('-o', '--output', 'output', type=click.File('w'), default=None)
def compile_json(src_json_file, output):
    """Compile source json file (resolve $ref)."""
    click.secho('Compile json file (resolve $ref): ', fg='green', nl=False)
    click.secho(src_json_file.name)
    data = jsonref.load(src_json_file)
    if not output:
        output = sys.stdout
    json.dump(data, fp=output, indent=2)
