# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2022 RERO
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

"""URN specific CLI commands."""


import click
from flask.cli import with_appcontext

from sonar.modules.documents.urn import Urn


@click.group()
def urn():
    """URN specific commands."""


@urn.command('register-urn-pids')
@with_appcontext
def register_urn_identifiers():
    """Register URN identifiers with status NEW."""
    urn_codes = Urn.get_unregistered_urns()
    if count := len(urn_codes):
        click.secho(f'Found  {count} urns to register', fg='yellow')
        registered = 0
        for urn_code in urn_codes:
            if Urn.register_urn(urn=urn_code):
                click.secho(
                    f'\turn code: {urn_code} successfully registered', fg='green')
                registered += 1
            else:
                click.secho(
                    f'\turn code: {urn_code} still pending', fg='red')

        click.secho(f'Found  {count} urns to register', fg='yellow')
        click.secho(
            f'Number URNs successfully registered: {registered}', fg='green')
        click.secho(
            f'Number URNs pending: {count-registered}', fg='red')
    else:
        click.secho('No urns found to register', fg='yellow')

