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
        return next(
            iter(next(iter(self.index.get_alias().values()))['aliases']))
