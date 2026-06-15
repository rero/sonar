# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Validation schema."""

from invenio_records.extensions import RecordExtension as BaseRecordExtension

from ..api import Validation


class ValidationExtension(BaseRecordExtension):
    """Record hooks class."""

    def pre_commit(self, record):
        """Hook executed before DB persistences.

        This method processes the validation on the record.
        Validation is only processed for organisations with validation workflow enabled.

        :param record: Record to check.
        """
        Validation().process(record)
