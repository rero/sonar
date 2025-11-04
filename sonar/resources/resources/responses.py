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

"""SONAR resources responses."""

from flask_resources.responses import ResponseHandler


class DynamicResponseHandler(ResponseHandler):
    """Dynamic response handler."""

    def __init__(self, serializer_factory, headers=None):
        """Dynamic response handler initialization.

        :param serializer_factory: A callable that returns a serializer.
        """
        self.serializer_factory = serializer_factory
        super().__init__(serializer=None, headers=headers)

    def make_response(self, obj_or_list, code, many=False):
        """Builds a response for one object."""
        self.serializer = self.serializer_factory()
        return super().make_response(obj_or_list, code, many=many)
