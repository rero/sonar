# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Document resolver."""

import jsonresolver
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record


# the host corresponds to the config value for the key JSONSCHEMAS_HOST
@jsonresolver.route("/api/documents/<pid>", host="sonar.ch")
def document_resolver(pid):
    """Resolve referenced document."""
    resolver = Resolver(pid_type="doc", object_type="rec", getter=Record.get_record)
    _, record = resolver.resolve(pid)

    if record.get("$schema"):
        del record["$schema"]

    return record
