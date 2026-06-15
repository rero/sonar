# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""JSON resolvers."""

import jsonresolver
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record

from ...config import JSONSCHEMAS_HOST
from .config import Configuration


@jsonresolver.route(Configuration.resolver_url, host=JSONSCHEMAS_HOST)
def json_resolver(pid):
    """Resolve record.

    :param str pid: PID value.
    :return: Record instance.
    :rtype: Record
    """
    resolver = Resolver(pid_type=Configuration.pid_type, object_type="rec", getter=Record.get_record)
    _, record = resolver.resolve(pid)

    record.pop("$schema", None)

    return record
