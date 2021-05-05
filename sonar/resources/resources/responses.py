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

"""SONAR resources responses."""

from flask import Response, make_response
from flask_resources.responses import Response as ResourceResponse


class StreamResponse(ResourceResponse):
    """Stream response."""

    filename = None

    def __init__(self, serializer=None, **kwargs):
        """Stream response initialization.

        Sets the filename for attachment if present in kwargs.

        :param serializer: Record serializer.
        """
        self.filename = kwargs.pop('filename', 'records')
        super().__init__(serializer)

    def make_list_response(self, content, code=200):
        """Builds a response for a list of objects.

        :param content: Content to send.
        :param code: Status code.
        :returns: Response object.
        """
        response = make_response(
            "" if content is None else Response(
                self.serializer.serialize_object_list(content)),
            code,
            self.make_headers(),
        )
        response.headers[
            'Content-Disposition'] = f'attachment; filename={self.filename}'
        return response
