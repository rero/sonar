# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""API for manipulating records."""

from uuid import uuid4

from flask import current_app
from invenio_db import db
from invenio_jsonschemas import current_jsonschemas
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.api import Record
from invenio_search.api import RecordsSearch
from sqlalchemy.orm.exc import NoResultFound


class SonarRecord(Record):
    """SONAR Record."""

    minter = None
    fetcher = None
    provider = None
    object_type = "rec"
    schema = None

    @classmethod
    def create(cls, data, id_=None, dbcommit=False, **kwargs):
        """Create a new record."""
        assert cls.minter
        assert cls.schema

        if not id_:
            id_ = uuid4()

        if "$schema" not in data:
            data["$schema"] = current_jsonschemas.path_to_url(
                "{schema}s/{schema}-v1.0.0.json".format(schema=cls.schema)
            )

        cls.minter(id_, data)

        record = super(SonarRecord, cls).create(data=data, id_=id_, **kwargs)

        if dbcommit:
            record.dbcommit()

        return record

    @classmethod
    def get_record_by_pid(cls, pid, with_deleted=False):
        """Get ils record by pid value."""
        assert cls.provider
        try:
            persistent_identifier = PersistentIdentifier.get(
                cls.provider.pid_type, pid
            )
            return super(SonarRecord, cls).get_record(
                persistent_identifier.object_uuid, with_deleted=with_deleted
            )
        except NoResultFound:
            return None
        except PIDDoesNotExistError:
            return None

    @classmethod
    def get_ref_link(cls, type, id):
        """Get $ref link for the given type of record."""
        return "https://{host}/api/{type}/{id}".format(
            host=current_app.config.get("JSONSCHEMAS_HOST"), type=type, id=id
        )

    def dbcommit(self):
        """Commit changes to db."""
        db.session.commit()


class SonarSearch(RecordsSearch):
    """Search Class SONAR."""

    class Meta:
        """Search only on item index."""

        index = "records"
