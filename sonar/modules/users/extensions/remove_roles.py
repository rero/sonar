# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""User record extension to delete roles."""

from invenio_records.extensions import RecordExtension


class DeleteRolesExtension(RecordExtension):
    """Remove roles from user account."""

    def post_delete(self, record, force=False):
        """Called after a record is deleted."""
        record.remove_roles()
