# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Documents minters."""

from .providers import DocumentIdProvider


def document_pid_minter(record_uuid, data):
    """Mint loan identifiers."""
    assert 'pid' not in data
    provider = DocumentIdProvider.create(
        object_type='rec',
        object_uuid=record_uuid,
    )
    data['pid'] = int(provider.pid.pid_value)
    return provider.pid
