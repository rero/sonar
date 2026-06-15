# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

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
