# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""SONAR CLI commands."""

import click

from .documents.cli import documents
from .institutions.cli import institutions


@click.group()
def fixtures():
    """Fixtures management commands."""


fixtures.add_command(documents)
fixtures.add_command(institutions)
