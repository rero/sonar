# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Organisation resolver."""

import jsonresolver
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record


# the host corresponds to the config value for the key JSONSCHEMAS_HOST
@jsonresolver.route("/api/organisations/<pid>", host="sonar.ch")
def organisation_resolver(pid):
    """Resolve referenced organisation."""
    resolver = Resolver(pid_type="org", object_type="rec", getter=Record.get_record)
    _, record = resolver.resolve(pid)

    if record.get("$schema"):
        del record["$schema"]

    return record
