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

"""Sitemap cli."""


import click
from flask import current_app
from flask.cli import with_appcontext

from sonar.modules.sitemap.sitemap import sitemap_generate


@click.group()
def sitemap():
    """Sitemap."""


@sitemap.command()
@click.option("-s", "--server-name", "server_name", required=True, default=None)
@with_appcontext
def generate(server_name):
    """Generate a sitemap.

    :param: server_name: organisation server name.
    """
    sitemap_generate(
        server_name, current_app.config.get("SONAR_APP_SITEMAP_ENTRY_SIZE", 10000)
    )
    click.secho(f"Generate sitemap for {server_name}", fg="green")
