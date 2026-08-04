# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Inveio stats signal receivers for record-view events."""

from datetime import UTC, datetime
from ipaddress import ip_address

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


def flag_invalid_ip_as_robot(doc):
    """Flag an event as a robot event when its IP address is not a valid IP.

    The address comes from the `X-Forwarded-For` header, so an unparsable value
    means that the client forged the header, which is not a real visit.

    :param doc: The event to process.
    :returns: The event, flagged as a robot if its IP address is invalid.
    """
    if ip := doc.get("ip_address"):
        try:
            ip_address(ip)
        except ValueError:
            doc["is_robot"] = True
    return doc
