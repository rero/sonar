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

from flask import Response
from flask import make_response as flask_make_response
from flask_resources.responses import ResponseHandler


class StreamResponseHandler(ResponseHandler):
    """Stream response."""

    filename = None

    def __init__(self, serializer, filename="records", headers=None):
        """Stream response initialization.

        :param filename: File name.
        :param serializer: Record serializer.
        """
        self.filename = filename
        super().__init__(serializer=serializer, headers=headers)

    def make_response(self, obj_or_list, code, many=False):
        """Builds a response for one object."""
        # If view returns a response, bypass the serialization.
        if isinstance(obj_or_list, Response):
            return obj_or_list

        # https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.make_response
        # (body, status, header)
        if many:
            serialize = self.serializer.serialize_object_list
        else:
            serialize = self.serializer.serialize_object

        response = flask_make_response(
            (
                ""
                if obj_or_list is None
                else Response(self.serializer.serialize_object_list(obj_or_list))
            ),
            code,
        )

        response.headers["Content-Disposition"] = (
            f"attachment; filename={self.filename}"
        )
        return response
