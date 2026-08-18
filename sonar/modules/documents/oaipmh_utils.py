# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Invenio OAIPMH server utils."""

from invenio_oaiserver import current_oaiserver
from invenio_pidstore.errors import PIDDoesNotExistError
from sqlalchemy.exc import NoResultFound

from sonar.suggestions.dumpers import FIELD as SUGGESTIONS_FIELD

from .dumpers import IndexerDumper


def getrecord_fetcher(record_uuid):
    """Fetch record data as dict for serialization.

    The OAI persistent identifier survives the deletion of its record, so it
    still resolves and points to a record that cannot be loaded anymore. As the
    repository declares `deletedRecord=no`, answer with `idDoesNotExist`.
    """
    try:
        record = current_oaiserver.record_cls.get_record(record_uuid)
    except NoResultFound:
        raise PIDDoesNotExistError("oai", None) from None

    record_dict = record.dumps(IndexerDumper())
    # The indexer dumper denormalizes the suggestable values, which are of no
    # use outside of the index.
    record_dict.pop(SUGGESTIONS_FIELD, None)
    record_dict["updated"] = record.updated
    return record_dict
