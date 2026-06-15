# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""HEG CLI commands."""

import click

from .harvest import harvest


@click.group()
def heg():
    """Commands for HEG."""


heg.add_command(harvest)
