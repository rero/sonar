# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Persistent identifier minters for organisation."""


def id_minter(record_uuid, data, provider, pid_key="pid", object_type="rec"):
    """Organisation minter which takes the code value as PID."""
    # Create persistent identifier
    provider = provider.create(object_type=object_type, object_uuid=record_uuid, pid_value=data.get("code"))

    pid = provider.pid
    data[pid_key] = pid.pid_value

    return pid
