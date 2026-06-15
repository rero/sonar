# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Persistent identifier minters for documents."""

from flask import current_app
from invenio_oaiserver.minters import oaiid_minter
from invenio_oaiserver.provider import OAIIDProvider
from invenio_pidstore.errors import PIDAlreadyExists, PIDDoesNotExistError

from sonar.modules.ark.api import Ark


def id_minter(record_uuid, data, provider, pid_key="pid", object_type="rec"):
    """Document PID minter."""
    # Create persistent identifier
    provider = provider.create(object_type=object_type, object_uuid=record_uuid, pid_value=data.get(pid_key))

    pid = provider.pid
    data[pid_key] = pid.pid_value

    # Mandatory to check if PID for OAI exists, as the minter is called twice
    # during API calls..
    try:
        oai_pid_value = current_app.config.get("OAISERVER_ID_PREFIX", "") + str(pid.pid_value)
        OAIIDProvider.get(oai_pid_value, "oai")
    except PIDDoesNotExistError:
        oaiid_minter(record_uuid, data)

    external_minters(record_uuid, data, pid_key)

    return pid


def external_minters(record_uuid, data, pid_key="pid"):
    """External minters.

    ARK.

    :param record_uuid: Record UUID.
    :param data: Record data.
    :param pid_key: PID key.
    """
    new_data = current_app.extensions.get("invenio-records").replace_refs(data.get("organisation", [{}])[0])
    naan = new_data.get("arkNAAN")

    if not data.get("harvested") and (ark := Ark(naan=naan)):
        try:
            pid = ark.create(data[pid_key], record_uuid=record_uuid)
            data.setdefault("identifiedBy", []).append({"type": "ark", "value": pid.pid_value})
        except PIDAlreadyExists:
            pass
