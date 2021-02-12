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

"""Base overdo class for DOJSON transformation."""

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

    def do(self, blob, ignore_missing=True, exception_handlers=None):
        """Store blob values and do transformation."""
        self.blob_record = blob

        return super(Overdo, self).do(blob,
                                      ignore_missing=ignore_missing,
                                      exception_handlers=exception_handlers)
