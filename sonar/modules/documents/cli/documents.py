# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Documents CLI commands."""

import click

from .oai import oai
from .urn import urn


@click.group()
def documents():
    """Commands for documents."""


documents.add_command(urn)
documents.add_command(oai)
