# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2021 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Persistent identifier minters for documents."""

from __future__ import absolute_import, print_function, unicode_literals

from flask import current_app
from invenio_oaiserver.minters import oaiid_minter
from invenio_oaiserver.provider import OAIIDProvider
from invenio_pidstore.errors import PIDAlreadyExists, PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from sonar.modules.ark.api import Ark


def id_minter(record_uuid, data, provider, pid_key='pid', object_type='rec'):
    """Document PID minter."""
    # Create persistent identifier
    provider = provider.create(object_type=object_type,
                               object_uuid=record_uuid,
                               pid_value=data.get(pid_key))

    pid = provider.pid
    data[pid_key] = pid.pid_value

    # Mandatory to check if PID for OAI exists, as the minter is called twice
    # during API calls..
    try:
        oai_pid_value = current_app.config.get('OAISERVER_ID_PREFIX',
                                               '') + str(pid.pid_value)
        OAIIDProvider.get(oai_pid_value, 'oai')
    except PIDDoesNotExistError:
        oaiid_minter(record_uuid, data)

    external_minters(record_uuid, data, pid_key)

    return pid


def external_minters(record_uuid, data, pid_key='pid'):
    """External minters.

    RERO DOC and ARK.

    :param record_uuid: Record UUID.
    :param data: Record data.
    :param pid_key: PID key.
    :returns: Created PID object.
    """
    for identifier in data.get('identifiedBy', []):
        if identifier.get('source') == 'RERO DOC':
            try:
                pid = PersistentIdentifier.create('rerod',
                                                  identifier['value'],
                                                  object_type='rec',
                                                  object_uuid=record_uuid,
                                                  status=PIDStatus.REGISTERED)
                pid.redirect(PersistentIdentifier.get('doc', data[pid_key]))
            except PIDAlreadyExists:
                pass
    new_data = current_app.extensions.get('invenio-records').replace_refs(data.get('organisation', [{}])[0])
    naan = new_data.get('arkNAAN')

    if not data.get('harvested') and (ark := Ark(naan=naan)):
        try:
            pid = ark.create(data[pid_key], record_uuid=record_uuid)
            data.setdefault('identifiedBy', []).append(
                dict(type='ark', value=pid.pid_value))
        except PIDAlreadyExists:
            pass
