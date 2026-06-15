# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Invenio OAIPMH server utils."""

from invenio_oaiserver import current_oaiserver

from .dumpers import IndexerDumper


def getrecord_fetcher(record_uuid):
    """Fetch record data as dict for serialization."""
    record = current_oaiserver.record_cls.get_record(record_uuid)
    record_dict = record.dumps(IndexerDumper())
    record_dict["updated"] = record.updated
    return record_dict
