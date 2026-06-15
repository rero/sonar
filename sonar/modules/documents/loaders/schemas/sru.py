# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""SRU schema."""

from marshmallow import fields, pre_dump

from ...dojson.sru.model import overdo
from .marc21 import Marc21Schema


class SRUSchema(Marc21Schema):
    """SRU marshmallow schema."""

    identifiedBy = fields.List(fields.Dict())
    language = fields.List(fields.Dict())
    title = fields.List(fields.Dict())
    abstracts = fields.List(fields.Dict())
    contentNote = fields.List(fields.Str())
    contribution = fields.List(fields.Dict())
    extent = fields.Str()
    dissertation = fields.Dict()
    additionalMaterials = fields.Str()
    formats = fields.List(fields.Str())
    otherMaterialCharacteristics = fields.Str()
    editionStatement = fields.Dict()
    documentType = fields.Str()
    provisionActivity = fields.List(fields.Dict())
    notes = fields.List(fields.Str())
    series = fields.List(fields.Dict())
    partOf = fields.List(fields.Dict())

    @pre_dump
    def process(self, obj, **kwargs):
        """All the process is done by overdo."""
        return overdo.do(obj)
