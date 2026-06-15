# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""User record extension to delete deposits."""

from invenio_records.extensions import RecordExtension


class DeleteDepositsExtension(RecordExtension):
    """Deletes associated deposits."""

    def post_delete(self, record, force=False):
        """Called after a record is deleted."""
        from sonar.modules.users.tasks import delete_deposits

        delete_deposits.delay(record["pid"], force=force, dbcommit=True, delindex=True)
