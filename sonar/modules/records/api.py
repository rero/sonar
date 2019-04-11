# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""API for records"""

import uuid
from invenio_pidstore.models import PersistentIdentifier
from invenio_pidstore.providers.recordid import RecordIdProvider
from invenio_pidstore.fetchers import FetchedPID

def record_id_minter(object_uuid, data):
    assert 'pid' not in data
    provider = RecordIdProvider.create(
        object_type='rec', object_uuid=object_uuid)
    data['pid'] = provider.pid.pid_value
    return provider.pid

def record_id_fetcher(object_uuid, data):
    return FetchedPID(
        provider=RecordIdProvider,
        pid_type=RecordIdProvider.pid_type,
        pid_value=str(data['pid'])
    )
