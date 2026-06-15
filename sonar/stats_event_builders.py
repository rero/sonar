# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Inveio stats signal receivers for record-view events."""

from datetime import UTC, datetime

from flask import request
from invenio_stats.utils import format_datetime_iso, get_user

from .modules.documents.api import DocumentRecord


def record_view_event_builder(event, sender_app, pid=None, record=None, **kwargs):
    """Build a record-view event."""
    if not isinstance(record, DocumentRecord):
        return None
    event.update(
        {
            # When:
            "timestamp": format_datetime_iso(datetime.now(UTC)),
            # What:
            "record_id": str(record.id),
            "pid_type": pid.pid_type,
            "pid_value": str(pid.pid_value),
            "referrer": request.referrer,
            # Who:
            **get_user(),
        }
    )
    return event
