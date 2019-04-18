# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Documents fetchers."""

from invenio_pidstore.fetchers import FetchedPID


def document_pid_fetcher(record_uuid, data):
    """Fetch PID from document record."""
    return FetchedPID(
        provider=None,
        pid_type='doc',
        pid_value=str(data['pid'])
    )
