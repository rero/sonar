# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Document dumpers."""

from copy import deepcopy

from invenio_records.api import _records_state
from invenio_records.dumpers import Dumper

from sonar.modules.utils import get_ips_list


class ReplaceRefsDumper(Dumper):
    """Replace linked resources in document."""

    def dump(self, record, data):
        """Dump a document instance with basic document information's.

        :param record: The record to dump.
        :param data: The initial dump data passed in by ``record.dumps()``.
        """
        from .api import DocumentRecord

        # do a fresh copy
        data = deepcopy(record)
        return deepcopy(DocumentRecord(_records_state.replace_refs(data)))


class IndexerDumper(Dumper):
    """Document indexer dumper."""

    @staticmethod
    def _add_dates(record, data):
        """Adds isOpenAccess field."""
        data["_created"] = record.created.isoformat() if record.created else None
        data["_updated"] = record.updated.isoformat() if record.updated else None

    @staticmethod
    def _replace_refs(data):
        """Adds isOpenAccess field."""
        return deepcopy(_records_state.replace_refs(data))

    @staticmethod
    def _process_open_access(record, data):
        """Adds isOpenAccess field."""
        # Check if record is open access.
        data["isOpenAccess"] = record.is_open_access()

    @staticmethod
    def _process_organisation_ips(record, data):
        """Adds isOpenAccess field."""
        # Compile allowed IPs in document
        if data.get("organisation"):
            if data["organisation"][0].get("allowedIps"):
                data["organisation"][0]["ips"] = get_ips_list(data["organisation"][0]["allowedIps"].split("\n"))
            else:
                data["organisation"][0]["ips"] = []

    @staticmethod
    def _process_fulltext(record, data):
        """Adds isOpenAccess field."""
        # No files are present in record
        if not record.files:
            return

        # Store fulltext in array for indexing
        data["fulltext"] = []
        for file in record.files:
            if file.get("type") == "fulltext":
                with file.file.storage().open() as pdf_file:
                    data["fulltext"].append(pdf_file.read().decode("utf-8"))

    @staticmethod
    def _process_identifiers(record, data):
        """Adds isOpenAccess field."""
        # No files are present in record
        for identifier in data.get("identifiedBy", []):
            data.setdefault("identifiers", {})
            key = identifier["type"].split(":")[-1].lower()
            data["identifiers"].setdefault(key, []).append(identifier["value"])

    def dump(self, record, data):
        """Dump a document instance with basic document information's.

        :param record: The record to dump.
        :param data: The initial dump data passed in by ``record.dumps()``.
        """
        data = deepcopy(record)
        data = self._replace_refs(data)
        self._add_dates(record, data)
        self._process_open_access(record, data)
        self._process_organisation_ips(record, data)
        self._process_fulltext(record, data)
        self._process_identifiers(record, data)

        return data


document_indexer_dumper = IndexerDumper()
