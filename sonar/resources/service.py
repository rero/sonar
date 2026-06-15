# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""SONAR resources base service class."""

from flask_principal import Identity, Need, UserNeed
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records_resources.services import (
    RecordServiceConfig as BaseRecordServiceConfig,
)
from invenio_records_resources.services.records import (
    RecordService as BaseRecordService,
)


class RecordServiceConfig(BaseRecordServiceConfig):
    """Service factory configuration."""


class RecordService(BaseRecordService):
    """SONAR resources base service class."""

    def create(self, identity, data, **kwargs):
        """Create a record.

        :param identity: Identity of user creating the record.
        :param data: Input data according to the data schema.
        """
        # TODO: Why Identity(1) and UserNeed(1) ???
        if not identity:
            identity = Identity(1)
            identity.provides.add(UserNeed(1))
            identity.provides.add(Need(method="system_role", value="any_user"))

        return super().create(identity, data, **kwargs)

    def bulk_reindex(self):
        """Send all records to the index queue and process indexing."""
        ids = (
            x[0]
            for x in PersistentIdentifier.query.filter_by(object_type="rec", status=PIDStatus.REGISTERED)
            .filter(PersistentIdentifier.pid_type.in_([self.record_cls.pid_type]))
            .values(PersistentIdentifier.object_uuid)
        )

        self.indexer.bulk_index(ids)
        self.indexer.process_bulk_queue()
