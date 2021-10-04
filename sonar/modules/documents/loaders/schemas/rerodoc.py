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

"""RERODOC schema."""

from invenio_records_rest.schemas.fields import SanitizedUnicode
from marshmallow import fields, pre_dump

from sonar.modules.documents.dojson.rerodoc.model import overdo

from .marc21 import Marc21Schema


class RerodocSchema(Marc21Schema):
    """RERODOC schema."""

    documentType = SanitizedUnicode()
    title = fields.List(fields.Dict())
    partOf = fields.List(fields.Dict())
    abstracts = fields.List(fields.Dict())
    contribution = fields.List(fields.Dict())
    organisation = fields.List(fields.Dict())
    language = fields.List(fields.Dict())
    copyrightDate = fields.List(fields.String())
    editionStatement = fields.Dict()
    provisionActivity = fields.List(fields.Dict())
    extent = SanitizedUnicode()
    otherMaterialCharacteristics = SanitizedUnicode()
    formats = fields.List(SanitizedUnicode())
    additionalMaterials = SanitizedUnicode()
    series = fields.List(fields.Dict())
    notes = fields.List(fields.String())
    identifiedBy = fields.List(fields.Dict())
    subjects = fields.List(fields.Dict())
    classification = fields.List(fields.Dict())
    collections = fields.List(fields.Dict())
    dissertation = fields.Dict()
    otherEdition = fields.List(fields.Dict())
    usageAndAccessPolicy = fields.Dict()
    files = fields.List(fields.Dict())
    subdivisions = fields.List(fields.Dict())
    customField1 = fields.List(fields.String())
    customField2 = fields.List(fields.String())
    customField3 = fields.List(fields.String())

    @pre_dump
    def process(self, obj, **kwargs):
        """All the process is done by overdo."""
        return overdo.do(obj)
