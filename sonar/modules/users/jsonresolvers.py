# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""User resolver."""

import jsonresolver
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record


# the host corresponds to the config value for the key JSONSCHEMAS_HOST
@jsonresolver.route("/api/users/<pid>", host="sonar.ch")
def user_resolver(pid):
    """Resolve referenced user."""
    resolver = Resolver(pid_type="user", object_type="rec", getter=Record.get_record)
    _, record = resolver.resolve(pid)

    del record["$schema"]
    return record
