# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Record from HEG."""

from sonar.heg.serializers.schemas.factory import SchemaFactory


class HEGRecord:
    """HEG record."""

    SOURCES_PRIORITY = ["Medline", "CrossRef", "unpaywall"]

    data = None

    def __init__(self, data):
        """Initialize record.

        :param data: record dictionary
        """
        self.data = data

    def serialize(self):
        """Serialize record from source data."""
        record = {}

        for source in self.SOURCES_PRIORITY:
            record_source_key = f"{source}_record"

            if self.data.get(record_source_key):
                record = dict(
                    SchemaFactory.create(source).dump(self.data[record_source_key]),
                    **record,
                )

        # If `oa_status` is `closed`, the first file is flagged as restricted.
        if record.get("files"):
            record["files"][0]["access"] = "coar:c_16ec" if record.get("oa_status") == "closed" else "coar:c_abf2"

        return record
