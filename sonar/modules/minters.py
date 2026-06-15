# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Persistent identifier minters."""


def id_minter(record_uuid, data, provider, pid_key="pid", object_type="rec"):
    """SONAR minter."""
    # Create persistent identifier
    provider = provider.create(object_type=object_type, object_uuid=record_uuid, pid_value=data.get(pid_key))

    pid = provider.pid
    data[pid_key] = pid.pid_value

    return pid
