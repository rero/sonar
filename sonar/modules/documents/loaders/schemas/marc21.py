# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Marc21 schema."""

from dojson.contrib.marc21.utils import create_record
from marshmallow import Schema, pre_dump


class Marc21Schema(Schema):
    """Marc21 marshmallow schema."""

    @pre_dump
    def parse_xml(self, data, **kwargs):
        """Parse xml data and convert into dictionary.

        :param data: XML string.
        :returns: DictDict.
        """
        return create_record(data)
