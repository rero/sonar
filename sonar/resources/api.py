# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""SONAR resources base API class."""

from invenio_records_resources.records.api import Record as BaseRecord
from werkzeug.utils import cached_property


class Record(BaseRecord):
    """Record base class."""

    @cached_property
    def index_name(self):
        """Return the name of the current index (alias).

        :returns: The alias of the current index.
        :rtype: str
        """
        return next(iter(next(iter(self.index.get_alias().values()))["aliases"]))
