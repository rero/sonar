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

"""Schema for exporting records."""

from marshmallow import Schema, fields


class ExportSchemaV1(Schema):
    """Schema for exporting records."""

    code = fields.String(dump_only=True)
    name = fields.String(dump_only=True)
    description = fields.List(fields.Dict(dump_only=True))
    footer = fields.List(fields.Dict(dump_only=True))
    isShared = fields.Boolean(dump_only=True)
    isDedicated = fields.Boolean(dump_only=True)
    files = fields.Method("get_files", dump_only=True)
    allowedIps = fields.String(dump_only=True)
    platformName = fields.String(dump_only=True)
    documentsCustomField1 = fields.Dict(dump_only=True)
    documentsCustomField2 = fields.Dict(dump_only=True)
    documentsCustomField3 = fields.Dict(dump_only=True)
    publicDocumentFacets = fields.List(fields.String(dump_only=True))

    def get_files(self, obj):
        """Get files."""
        files = []
        for file in obj.files:
            json = file.dumps()
            json["uri"] = file.file.uri
            files.append(json)

        return files
