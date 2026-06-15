# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

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
