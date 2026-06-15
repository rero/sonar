# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

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
    sitemap_generate(server_name, current_app.config.get("SONAR_APP_SITEMAP_ENTRY_SIZE", 10000))
    click.secho(f"Generate sitemap for {server_name}", fg="green")
