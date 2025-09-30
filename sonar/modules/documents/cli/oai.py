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
