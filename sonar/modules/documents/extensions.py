# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""DocumentRecord Extensions."""

import contextlib

from flask import current_app
from invenio_db import db
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.extensions import RecordExtension

from sonar.modules.documents.urn import Urn


class ArkDocumentExtension(RecordExtension):
    """Register/unregister Ark identifiers."""

    def post_delete(self, record, force=False):
        """Called after a record is deleted.

        :param record: the invenio record instance to be processed.
        :param force: unused.
        """
        if ark_id := record.get_ark():
            with contextlib.suppress(PIDDoesNotExistError):
                PersistentIdentifier.get("ark", ark_id).delete()


class UrnDocumentExtension(RecordExtension):
    """Create URN identifiers."""

    def pre_create(self, record):
        """Called before a record is created.

        :param record: the invenio record instance to be processed.
        """
        # Generate URN codes for documents without URNs.
        if not record.get_rero_urn_code(record):
            Urn.create_urn(record)
        if record.model:
            with db.session.begin_nested():
                record.model.data = record
                db.session.add(record.model)

    def post_create(self, record):
        """Called after a record is created.

        :param record: the invenio record instance to be processed.
        """
        try:
            Urn.register_urn_code_from_document(record)
        except Exception as e:
            current_app.logger.error(f"Error during URN registration{e}")

    def post_delete(self, record, force=False):
        """Called after a record is deleted.

        :param record: the invenio record instance to be processed.
        :param force: unused.
        """
        from .api import DocumentRecord

        if urn_code := DocumentRecord.get_rero_urn_code(record):
            with contextlib.suppress(PIDDoesNotExistError):
                urn_pid = PersistentIdentifier.get("urn", urn_code)
                urn_pid.delete()
                current_app.logger.error(
                    f"Document (pid:{record['pid']}) has been deleted and contains an URN ({urn_code})"
                )
