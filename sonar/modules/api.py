# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""API for manipulating records."""

from uuid import uuid4

from invenio_jsonschemas import current_jsonschemas
from invenio_records.api import Record


class SonarRecord(Record):
    """SONAR Record."""

    minter = None
    fetcher = None
    provider = None
    object_type = 'rec'
    schema = None

    @classmethod
    def create(cls, data, id_=None, **kwargs):
        """Create a new record."""
        assert cls.minter
        assert cls.schema

        if not id_:
            id_ = uuid4()

        if '$schema' not in data:
            data["$schema"] = current_jsonschemas.path_to_url(
                '{0}s/{0}-v1.0.0.json'.format(cls.schema))

        print(data)
        cls.minter(id_, data)

        return super(SonarRecord, cls).create(data=data, id_=id_, **kwargs)
