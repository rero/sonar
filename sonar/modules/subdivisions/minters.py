# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Minters."""


def id_minter(record_uuid, data, provider, pid_key="pid", object_type="rec"):
    """PID minter.

    :param str record_uuid: UUID of the record
    :param dict data: Data of the record
    :param RecordProvider provider: PID provider
    :param str pid_key: PIF key
    :param str object_type: Object type
    :return: PID value
    :rtype: str
    """
    # Create persistent identifier
    provider = provider.create(object_type=object_type, object_uuid=record_uuid, pid_value=data.get(pid_key))
    pid = provider.pid
    data[pid_key] = pid.pid_value
    return pid
