# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Project resolver."""

import jsonresolver

from sonar.proxies import sonar


# the host corresponds to the config value for the key JSONSCHEMAS_HOST
@jsonresolver.route("/api/projects/<pid>", host="sonar.ch")
def project_resolver(pid):
    """Resolve referenced project.

    This resolver is kept for compatibility reason with old resource
    management.
    """
    record = sonar.service("projects").record_cls.pid.resolve(pid)

    data = {"pid": record["id"], "name": record["metadata"]["name"]}

    if record["metadata"].get("investigators"):
        data["investigators"] = record["metadata"]["investigators"]

    return data
