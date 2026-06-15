# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Celery tasks for stats."""

from celery import shared_task

from .api import Record


@shared_task()
def collect_stats():
    """Collect and store the current statistics."""
    record = Record.collect()
    return f"New stat has been created with a pid of: {record['pid']}"
