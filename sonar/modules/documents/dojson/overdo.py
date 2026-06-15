# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Base overdo class for DOJSON transformation."""

import re

from dojson import Overdo as BaseOverdo


class Overdo(BaseOverdo):
    """Base overdo class for DOJSON transformation."""

    blob_record = None
    result_ok = True

    @staticmethod
    def not_repetitive(value, subfield, default=None):
        """Get the first value if the value is a list or tuple."""
        data = value.get(subfield, default)

        if isinstance(data, (list, tuple)):
            data = data[0]

        return data

    @staticmethod
    def extract_date(date=None):
        """Try to extract date of birth and date of death from field.

        :param date: String, date to parse
        :returns: Tuple containing date of birth and date of death
        """
        if not date:
            return (None, None)

        # Match a full date
        match = re.search(r"^([0-9]{4}-[0-9]{2}-[0-9]{2})$", date)
        if match:
            return (match.group(1), None)

        match = re.search(r"^([0-9]{2}-[0-9]{2}-[0-9]{4})$", date)
        if match:
            return (match.group(1), None)

        # Match these value: "1980-2010"
        match = re.search(r"^([0-9]{4})-([0-9]{4})$", date)
        if match:
            return (match.group(1), match.group(2))

        # Match these value: "1980-" or "1980"
        match = re.search(r"^([0-9]{4})-?", date)
        if match:
            return (match.group(1), None)

        raise Exception(f'Date "{date}" is not recognized')

    def do(self, blob, ignore_missing=True, exception_handlers=None):
        """Store blob values and do transformation."""
        self.blob_record = blob

        return super().do(blob, ignore_missing=ignore_missing, exception_handlers=exception_handlers)
