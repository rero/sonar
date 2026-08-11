# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Suggestions dumpers."""

from invenio_records.dumpers import SearchDumperExt

# Nested field added to the indexed data, see the `autocomplete` analyzer in the
# `record.json` ES template and the `suggestions` property of the mappings.
FIELD = "suggestions"


class SuggestionsDumperExt(SearchDumperExt):
    """Denormalize the suggestable values of a record.

    Each value gets its own sub-document, so that Elasticsearch matches and
    aggregates the values individually instead of matching the record as a
    whole. Any resource can reuse it with the paths of its own fields.
    """

    def __init__(self, fields):
        """Initialize the extension.

        :param fields: paths of the suggestable fields in the dumped data.
        """
        self.fields = fields

    @classmethod
    def _extract_values(cls, data, parts):
        """Collect the string values reachable through a field path.

        Lists are walked at any level, as arrays of objects are common in the
        schemas, ie. `contribution.agent.preferred_name`.

        :param data: portion of the data to walk.
        :param parts: remaining parts of the field path.
        :returns: generator over the string values found.
        """
        if isinstance(data, list):
            for item in data:
                yield from cls._extract_values(item, parts)
        elif not parts:
            if isinstance(data, str):
                yield data
        elif isinstance(data, dict):
            yield from cls._extract_values(data.get(parts[0]), parts[1:])

    def dump(self, record, data):
        """Add the nested suggestions to the data to index.

        :param record: the record to dump.
        :param data: the data to index.
        """
        data[FIELD] = [
            {"field": field, "value": value}
            for field in self.fields
            for value in dict.fromkeys(self._extract_values(data, field.split(".")))
        ]

    def load(self, data, record_cls):
        """Remove the nested suggestions from the indexed data.

        The mappings already exclude them from the stored source, this keeps
        them out of the record should an index escape the reindex.

        :param data: the indexed data.
        :param record_cls: the record class.
        """
        data.pop(FIELD, None)
