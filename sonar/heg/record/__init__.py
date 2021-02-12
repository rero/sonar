# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2021 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Record from HEG."""

from slugify import slugify

from sonar.heg.serializers.schemas.factory import SchemaFactory
from sonar.modules.organisations.api import OrganisationRecord


class HEGRecord():
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
            record_source_key = "{source}_record".format(source=source)

            if self.data.get(record_source_key):
                record = dict(
                    SchemaFactory.create(source).dump(
                        self.data[record_source_key]), **record)

        # Flag as hidden if no file provided
        if not record.get('files'):
            record['hiddenFromPublic'] = True

        return record
