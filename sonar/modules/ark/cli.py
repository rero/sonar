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

import json

import click
from flask.cli import with_appcontext

from .api import NMAServerError, NMAUnauthorizedError, current_ark


@click.group()
@with_appcontext
def ark():
    """ARK utils commands."""
    if not current_ark:
        click.secho('ARK is not enabled.', fg='red')
        raise click.Abort()

@ark.command()
@with_appcontext
def status():
    """Check the ARK NMA status."""
    try:
        message = current_ark.status()
        click.secho(f'message: {message}', fg='green')
    except NMAServerError as e: # pragma: no cover
        click.secho(f'{e}', fg='red')

@ark.command()
@with_appcontext
@click.argument('ark')
def get(ark):
    """Get the ARK informations given an id."""
    try:
        data = json.dumps(current_ark.get(ark), indent=2)
        click.secho(f'{data}', fg='green')
    except NMAServerError as e: # pragma: no cover
        click.secho(f'{e}', fg='red')

@ark.command()
@with_appcontext
@click.argument('ark')
def resolve(ark):
    """Resolve an ARK id."""
    try:
        message = current_ark.resolve(ark)
        click.secho(f'{message}', fg='green')
    except NMAServerError as e: # pragma: no cover
        click.secho(f'{e}', fg='red')

@ark.command()
@with_appcontext
def login():
    """Check NMA login."""
    try:
        message = current_ark.login()
        click.secho(f'{message}', fg='green')
    except (NMAServerError, NMAUnauthorizedError) as e:
        click.secho(f'{e}', fg='red')

@ark.command()
@with_appcontext
def config():
    """Dump the ARK client configurations."""
    click.secho(f'{current_ark.config()}')

@ark.command()
@with_appcontext
@click.argument('target')
def mint(target):
    """Generate and register a new ARK id."""
    try:
        message = current_ark.mint(target)
        click.secho(f'{message}', fg='green')
    except (NMAServerError, NMAUnauthorizedError) as e:
        click.secho(f'{e}', fg='red')

@ark.command()
@with_appcontext
@click.argument('identifier')
@click.argument('target')
def create(identifier, target):
    """Create an new ARK with a given id."""
    try:
        message = current_ark.create(identifier, target, update_if_exists='yes')
        click.secho(f'{message}', fg='green')
    except (NMAServerError, NMAUnauthorizedError) as e:
        click.secho(f'{e}', fg='red')

@ark.command()
@with_appcontext
@click.argument('identifier')
@click.argument('target')
def update(identifier, target):
    """Update the given ARK."""
    try:
        message = current_ark.update(identifier, target)
        click.secho(f'{message}', fg='green')
    except (NMAServerError, NMAUnauthorizedError) as e:
        click.secho(f'{e}', fg='red')

@ark.command()
@with_appcontext
@click.argument('identifier')
def delete(identifier):
    """Mark an ARK as unavailable."""
    try:
        message = current_ark.delete(identifier)
        click.secho(f'{message}', fg='green')
    except (NMAServerError, NMAUnauthorizedError) as e:
        click.secho(f'{e}', fg='red')
