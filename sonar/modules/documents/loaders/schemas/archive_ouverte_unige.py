# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Archive ouverte UNIGE schema."""

from marshmallow import fields, pre_dump

from sonar.modules.documents.dojson.archive_ouverte_unige.model import overdo

from .marc21 import Marc21Schema


class ArchiveOuverteUnigeSchema(Marc21Schema):
    """Archive ouverte UNIGE schema."""

    identifiedBy = fields.List(fields.Dict())
    title = fields.List(fields.Dict())

    @pre_dump
    def process(self, obj, **kwargs):
        """All the process is done by overdo."""
        return overdo.do(obj)
